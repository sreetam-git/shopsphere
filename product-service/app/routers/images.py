import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_db
from ..models import Product, ProductVariant, ProductImage
from ..schemas import ProductImageResponse
from ..storage import upload_file_to_s3, delete_file_from_s3

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

@router.post("/{product_id}/images", response_model=ProductImageResponse, status_code=201)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    variant_id: int | None = Form(default=None),
    alt_text: str | None = Form(default=None),
    display_order: int = Form(default=0),
    db: Session = Depends(get_db)
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
            pass

        raise HTTPException(
            500,
            "Failed to save image metadata"
        )

    return image_record