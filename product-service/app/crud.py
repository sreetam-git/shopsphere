from sqlalchemy.orm import Session

from .models import Category
from .schemas import CategoryCreate

def create_category(db: Session, category: CategoryCreate):
    db_category = Category(
        name = category.name,
        description = category.description
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category

def fetch_categories(db: Session):
    categories = db.query(Category).all()
    return categories

def get_category_by_id(db: Session, id: int):
    category = db.query(Category).filter(Category.id == id).first()
    return category

def update_category_by_id(db: Session, category_id: int, category_data: CategoryCreate):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        return None

    category.name = category_data.name
    category.description = category_data.description
    db.commit()
    db.refresh(category)

    return category

def delete_category_by_id(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        return None

    if category.products:
        return "has_products"

    db.delete(category)
    db.commit()

    return category