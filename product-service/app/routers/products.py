from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..crud import (create_product, 
                    get_products_list, 
                    get_product_by_id, 
                    update_product_by_id, 
                    delete_product_by_id,
                    create_product_attribute,
                    update_product_attribute_byid,
                    get_product_attributes,
                    fetch_product_variant_options,
                    create_bulk_variants,
                    fetch_product_variants_by_id
                    )
from ..schemas import (ProductCreate, 
                       ProductUpdate, 
                       ProductResponse, 
                       ProductAttributeResponse,
                       ProductAttributeAssign,
                       ProductVariantResponse,
                       VariantOptionResponse,
                       ProductVariantBulkCreate,
                       ProductVariantDetailResponse
                       )

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def add_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    result = create_product(db, product_data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return result

@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = get_products_list(db)
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def get_product_details(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    return product

@router.put('/{product_id}', response_model=ProductResponse)
def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)):
    product = update_product_by_id(db, product_data, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category Not found"
        )

    if product == "product_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product Not found"
        )

    return product

@router.delete("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    result = delete_product_by_id(db, product_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    return result

# assign attributes to the product
@router.post("/{product_id}/attributes", response_model=ProductAttributeResponse)
def add_product_attribute(product_id: int, attribute_data: ProductAttributeAssign, db: Session = Depends(get_db)):
    result = create_product_attribute(db, product_id, attribute_data)
    if result == "product_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product Not Found"
        )
    elif result == "attribute_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute Not Found"
        )
    elif result == "already_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attribute already exists"
        )

    return result

# fetch all product assigned attributes
@router.get("/{product_id}/attributes", response_model=list[ProductAttributeResponse])
def fetch_product_attributes(product_id: int, db: Session = Depends(get_db)):
    result = get_product_attributes(db, product_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    return result

# Update the assigned attribute
@router.put("/{product_id}/attributes", response_model=ProductAttributeResponse)
def update_product_attribute(product_id: int, attribute_data: ProductAttributeAssign, db: Session = Depends(get_db)):
    result = update_product_attribute_byid(db, product_id, attribute_data)
    if result == "product_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product Not Found"
        )
    elif result == "attribute_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute Not Found"
        )
    elif result == "assignment_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute with this product does not exist."
        )

    return result

# fetch variant options
@router.get("/{product_id}/variant-options", response_model=list[VariantOptionResponse])
def get_variant_options(product_id: int, db: Session = Depends(get_db)):
    result = fetch_product_variant_options(db, product_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="product not found"
        )
    elif result == "no_assignments":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignments not found"
        )

    return result

@router.post("/{product_id}/variants/bulk", response_model=list[ProductVariantResponse], status_code=status.HTTP_201_CREATED)
def create_product_variants_bulk(product_id: int, variant_data: ProductVariantBulkCreate, 
                                 db: Session = Depends(get_db)):
    result = create_bulk_variants(db, product_id, variant_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    elif result == "duplicate_sku":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate sku in the request"
        )
    elif result == "sku_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists"
        )
    elif result == "duplicate_attribute_values":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate attribute values in the request."
        )
    elif result == "attribute_value_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute value not found."
        )
    elif result == "duplicate_attributes":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate attributes found in request."
        )
    elif result == "missing_attribute_from_request":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select all the attributes"
        )
    elif result == "duplicate_combination":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Same combination of attribute values found."
        )
    elif result == "combination_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Variant already exists"
        )
    elif result == "conflict":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to save the variant"
        )

    return result

# Fetch all product variants with attributes
@router.get("/{product_id}/variants", response_model=list[ProductVariantDetailResponse])
def get_product_variants(product_id: int, db: Session = Depends(get_db)):
    result = fetch_product_variants_by_id(db, product_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product not found."
        )

    return result
    