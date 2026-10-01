from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import CategoryCreate, CategoryResponse
from ..crud import create_category, fetch_categories, get_category_by_id, update_category_by_id, delete_category_by_id

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/", response_model=CategoryResponse)
def add_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db=db, category=category)

@router.get("/", response_model=list[CategoryResponse], status_code=status.HTTP_200_OK)
def get_categories(db: Session = Depends(get_db)):
    result = fetch_categories(db=db)
    return result

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    result = get_category_by_id(db, category_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )

    return result

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryCreate, db: Session = Depends(get_db)):
    result = update_category_by_id(db, category_id, category_data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    return result

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    result = delete_category_by_id(db, category_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    if result == "has_products":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category because products are associated with it"
        )

    return {
        "message": "Category deleted successfully."
    }