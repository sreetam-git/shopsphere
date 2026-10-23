import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_db
from ..models import Product, ProductVariant, ProductImage
from ..schemas import ProductImageResponse
from ..storage import upload_file_to_s3, delete_file_from_s3, generate_presigned_url
from ..auth import get_current_admin
import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["Product Images"]
)

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def serialize_image(image: ProductImage) -> ProductImageResponse:
    return ProductImageResponse(
        id=image.id,
        product_id=image.product_id,
        variant_id=image.variant_id,
        alt_text=image.alt_text,
        is_primary=image.is_primary,
        storage_key=image.storage_key,
        display_order=image.display_order,
        image_url=generate_presigned_url(image.storage_key)
    )

@router.post("/{product_id}/images", response_model=ProductImageResponse, status_code=201)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    variant_id: int | None = Form(default=None),
    alt_text: str | None = Form(default=None),
    display_order: int = Form(default=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            404,
            "Product not found."
        )

    if variant_id is not None:
        variant = db.query(ProductVariant).filter(
            ProductVariant.id == variant_id,
            ProductVariant.product_id == product_id
        ).first()

        if not variant:
            raise HTTPException(
                404,
                "Variant Not Found"
            )

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            415,
            "Only JPEG, PNG, and WebP images are allowed"
        )

    if display_order < 0:
        raise HTTPException(
            422,
            "display_order cannot be negative"
        )

    contents = await file.read(MAX_FILE_SIZE + 1)
    if not contents:
        raise HTTPException(400, "Uploaded file is empty")

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(413, "Image must be 5 MB or smaller")

    #verify that the file content type matches the allowed file format

    try:
        from PIL import Image
        from io import BytesIO

        with Image.open(BytesIO(contents)) as image:
            image.verify()

        detected_format = Image.open(BytesIO(contents)).format
    except Exception:
        raise HTTPException(415, "Invalid image file")

    expected_formats = {
        "image/jpeg": "JPEG",
        "image/png": "PNG",
        "image/webp": "WEBP",
    }

    if detected_format != expected_formats[file.content_type]:
        raise HTTPException(
            415,
            "Image content does not match the declared file type"
        )

    extension = ALLOWED_TYPES[file.content_type]
    object_key = (
        f"products/{product_id}"
        f"{uuid.uuid4().hex}{extension}"
    )

    # call the upload function in the storage
    try:
        upload_file_to_s3(
            contents,
            object_key,
            file.content_type
        )
    except Exception:
        raise HTTPException(502, "Failed to upload image to storage")

    # now save the object key to database
    image_record = ProductImage(
        product_id = product_id,
        variant_id = variant_id,
        storage_key = object_key,
        alt_text = alt_text,
        display_order = display_order,
        is_primary = False
    )

    try:
        db.add(image_record)
        db.commit()
        db.refresh(image_record)
    except SQLAlchemyError:
        db.rollback()

        try:
            delete_file_from_s3(object_key)
        except Exception:
            logger.exception(
                "Failed to clean up S3 object after metadata save failed: key=%s",
                object_key,
            )

        raise HTTPException(
            500,
            "Failed to save image metadata"
        )

    return serialize_image(image_record)

@router.get("/{product_id}/images", response_model=list[ProductImageResponse])
def get_product_images(product_id: int, variant_id: int | None = None, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            404,
            "Product Not Found"
        )

    query = db.query(ProductImage).filter(
        ProductImage.product_id == product_id
    )

    # check for variant
    if variant_id is not None:
        print("***************************\n")
        print(f"variant id: {variant_id}")
        variant = db.query(ProductVariant).filter(
            ProductVariant.product_id == product_id,
            ProductVariant.id == variant_id
        ).first()

        if not variant:
            raise HTTPException(
                404,
                "Variant Not Found"
            )

        query = query.filter(ProductImage.variant_id == variant_id)

    images = query.order_by(
        ProductImage.display_order,
        ProductImage.id
    ).all()

    return [serialize_image(image) for image in images]

@router.patch("/{product_id}/images/{image_id}/primary", response_model=ProductImageResponse)
def set_primary_image(product_id: int, image_id: int, db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_admin)):
    image = db.query(ProductImage).filter(
        ProductImage.id == image_id,
        ProductImage.product_id == product_id
    ).first()

    if not image:
        raise HTTPException(
            404,
            "Image Not Found"
        )

    try:
        db.query(ProductImage).filter(
                ProductImage.product_id == product_id,
                ProductImage.variant_id == image.variant_id,
                ProductImage.is_primary.is_(True)
            ).update(
                {
                    ProductImage.is_primary: False
                },
                synchronize_session=False
            )
        
            # update the selected image status
        image.is_primary = True
        
        db.commit()
        db.refresh(image)

    except Exception:
        db.rollback()
        raise HTTPException(500, "Failed to update primary image.")

    return serialize_image(image)

@router.delete("/{product_id}/images/{image_id}")
def delete_product_image(product_id: int, image_id: int, db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_admin)):
    # find the image belonging to the product
    image = db.query(ProductImage).filter(
        ProductImage.id == image_id,
        ProductImage.product_id == product_id
    ).first()

    if not image:
        raise HTTPException(
            404,
            "Image not found."
        )

    object_key = image.storage_key
    variant_id = image.variant_id
    was_primary = image.is_primary

    try:
        # check for primary
        if was_primary:
            another_image = db.query(ProductImage).filter(
                ProductImage.variant_id == variant_id,
                ProductImage.product_id == product_id,
                ProductImage.is_primary.is_(False)
            ).order_by(ProductImage.display_order).first()

            if another_image:
                another_image.is_primary = True

        # delete the image
        db.delete(image)
        db.commit()

    except Exception:
        db.rollback()
        logger.exception("Failed to delete image metadata: image_id=%s", image_id,)

        raise HTTPException(
            status_code=500,
            detail="Failed to delete image metadata.",
        )

    # Delete the actual image file from s3
    try:
        delete_file_from_s3(object_key)
    except Exception:
        logger.info(
            "S3 cleanup failed for object key: %s",
            object_key,
        )

        return {
            "message": (
                "Image metadata was deleted, but S3 cleanup failed."
                "Manual cleanup is required."
            ),
            "image_id": image_id,
            "storage_cleanup": "failed"
        }

    logger.info(f"Image deleted successfully: {image_id}")
    return {
        "message": "Image deleted successfully.",
        "image_id": image_id,
        "storage_cleanup": "completed",
    }
