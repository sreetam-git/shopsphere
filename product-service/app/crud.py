from sqlalchemy.orm import Session

from .models import Category, Product, Attribute, AttributeValue, ProductVariant
from .schemas import (CategoryCreate, 
                      ProductCreate, 
                      ProductUpdate, 
                      AttributeCreate, 
                      AttributeValueCreate,
                      ProductVariantCreate
                      )

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

# add product attribute
def create_product_attribute(db: Session, product_id: int, attribute_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return "product_not_found"

    attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if not attribute:
        return "attribute_not_found"

    if attribute in product.attributes:
        return "already_exists"

    product.attributes.append(attribute)
    db.commit()

    return attribute

# get all product attributes
def get_product_attributes(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    return product.attributes

# attribute create
def create_attribute(db: Session, attribute_data: AttributeCreate):
    existing = db.query(Attribute).filter(Attribute.name == attribute_data.name).first()
    if existing:
        return None
    
    attr = Attribute(
        name = attribute_data.name
    )

    db.add(attr)
    db.commit()
    db.refresh(attr)
    return attr

# get all attributes
def fetch_attributes(db: Session):
    return db.query(Attribute).all()

# get attribute details
def get_attribute_by_id(db: Session, attribute_id: int):
    attr = db.query(Attribute).filter(Attribute.id == attribute_id).first()

    if not attr:
        return None

    return attr

# create attribute values
def create_attribute_value(db: Session, attribute_id: int, value_data: AttributeValueCreate):
    attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if not attribute:
        return None

    existing_value = (
        db.query(AttributeValue)
        .filter(
            AttributeValue.attribute_id == attribute_id,
            AttributeValue.value == value_data.value
            )
        .first()
        )

    if existing_value:
        return "value_exists"

    attr_value = AttributeValue(
        attribute_id = attribute_id,
        value = value_data.value
    )

    db.add(attr_value)
    db.commit()
    db.refresh(attr_value)

    return attr_value


def get_attribute_values_by_id(db: Session, attribute_id: int):
    attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if not attribute:
        return None

    attr_value = (
        db.query(AttributeValue)
        .filter(
            AttributeValue.attribute_id == attribute_id,
            )
        .all()
        )

    return attr_value

# create product variant
def create_variant(db: Session, product_id: int, variant_data: ProductVariantCreate):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return "product_not_found"

    exists = db.query(ProductVariant).filter(ProductVariant.sku == variant_data.sku).first()
    if exists:
        return "variant_exists"

    variant = ProductVariant(
        product_id = product_id,
        sku = variant_data.sku,
        price = variant_data.price,
        stock = variant_data.stock
    )

    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant