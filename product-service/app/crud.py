from sqlalchemy.orm import Session

from .models import Category, Product
from .schemas import CategoryCreate, ProductCreate, ProductUpdate

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


# Product CRUD
def create_product(db: Session, product_data: ProductCreate):
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        return None
    
    product = Product(
        name = product_data.name,
        description = product_data.description,
        category_id = product_data.category_id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product

# get products
def get_products_list(db: Session):
    products = db.query(Product).all()
    return products

# get product details
def get_product_by_id(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    return product

# product update
def update_product_by_id(db: Session, product_data: ProductUpdate, product_id: int):
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        return None

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return "product_not_found"

    product.name = product_data.name
    product.description = product_data.description
    product.category_id = product_data.category_id
    
    db.commit()
    db.refresh(product)

    return product

# product delete
def delete_product_by_id(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    product.is_active = False
    db.commit()
    db.refresh(product)

    return product