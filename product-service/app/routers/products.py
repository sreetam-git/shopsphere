from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..crud import (create_product, 
                    get_products_list, 
                    get_product_by_id, 
                    update_product_by_id, 
                    delete_product_by_id,
                    create_product_attribute,
                    get_product_attributes,
                    create_variant
                    )
from ..schemas import (ProductCreate, 
                       ProductUpdate, 
                       ProductResponse, 
                       ProductAttributeResponse,
                       ProductVariantResponse,
                       ProductVariantCreate
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

@router.post("/{product_id}/attributes/{attribute_id}", response_model=ProductAttributeResponse)
def add_product_attribute(product_id: int, attribute_id: int, db: Session = Depends(get_db)):
    result = create_product_attribute(db, product_id, attribute_id)
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

@router.get("/{product_id}/attributes", response_model=list[ProductAttributeResponse])
def fetch_product_attributes(product_id: int, db: Session = Depends(get_db)):
    result = get_product_attributes(db, product_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    return result

@router.post("/{product_id}/variants", response_model=ProductVariantResponse)
def add_variant(product_id: int, variant_data: ProductVariantCreate, db: Session = Depends(get_db)):
    result = create_variant(db, product_id, variant_data)
    if result == "product_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="product not found"
        )
    elif result == "variant_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Variant already exists"
        )

    return result
    