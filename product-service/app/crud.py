from sqlalchemy.orm import Session

from .models import Category, Product, Attribute, AttributeValue, ProductVariant, ProductAttribute
from .schemas import (CategoryCreate, 
                      ProductCreate, 
                      ProductUpdate, 
                      AttributeCreate, 
                      ProductAttributeAssign,
                      ProductAttributeResponse,
                      AttributeValueCreate,
                      VariantOptionValueResponse,
                      VariantOptionResponse,
                      ProductVariantBulkCreate,
                      ProductVariantDetailResponse
                      )

from sqlalchemy.exc import IntegrityError

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
def create_product_attribute(db: Session, product_id: int, attribute_data: ProductAttributeAssign):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return "product_not_found"

    attribute = db.query(Attribute).filter(Attribute.id == attribute_data.attribute_id).first()
    if not attribute:
        return "attribute_not_found"

    already_exists = (db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product_id,
        ProductAttribute.attribute_id == attribute_data.attribute_id
    ).first()
    )
    if already_exists:
        return "already_exists"

    p_attr = ProductAttribute(
        product_id = product_id,
        attribute_id = attribute_data.attribute_id,
        is_variant_attribute = attribute_data.is_variant_attribute
    )

    db.add(p_attr)
    db.commit()
    db.refresh(p_attr)

    return ProductAttributeResponse( 
        id=attribute.id, 
        name=attribute.name, 
        is_variant_attribute=p_attr.is_variant_attribute 
        )

# update product attribute
def update_product_attribute_byid(db: Session, product_id: int, attribute_data: ProductAttributeAssign):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return "product_not_found"

    attribute = db.query(Attribute).filter(Attribute.id == attribute_data.attribute_id).first()
    if not attribute:
        return "attribute_not_found"

    assignment = (db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product_id,
        ProductAttribute.attribute_id == attribute_data.attribute_id
    ).first()
    )
    if not assignment:
        return "assignment_not_found"

    assignment.is_variant_attribute = attribute_data.is_variant_attribute
    db.commit()
    db.refresh(assignment)

    return ProductAttributeResponse(
        id=assignment.attribute.id,
        name=assignment.attribute.name,
        is_variant_attribute=assignment.is_variant_attribute
    )

    

# get all product attributes
def get_product_attributes(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    assignments = db.query(ProductAttribute).filter( ProductAttribute.product_id == product_id ).all() 
    return [ 
        ProductAttributeResponse( 
            id=item.attribute.id, 
            name=item.attribute.name, 
            is_variant_attribute=item.is_variant_attribute 
            ) 
            for item in assignments 
        ]

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

# fetch all the attributes configured for variant
def fetch_product_variant_options(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    assignments = (db.query(ProductAttribute)
                  .filter(
                      ProductAttribute.product_id == product_id,
                      ProductAttribute.is_variant_attribute.is_(True)
                      )
                  .all()
                  )
    if not assignments:
        return "no_assignments"

    response = []
    for assignment in assignments:
        attribute = assignment.attribute

        values = (
            db.query(AttributeValue)
            .filter(
                AttributeValue.attribute_id == attribute.id
            )
            .order_by(AttributeValue.id)
            .all()
        )

        response.append(
            VariantOptionResponse(
                id=attribute.id,
                name=attribute.name,
                values= [
                    VariantOptionValueResponse(
                        id=value.id,
                        value=value.value
                    )
                    for value in values
                ]
            )
        )

        return response

# create bulk product variant
def create_bulk_variants(db: Session, product_id: int, variant_data: ProductVariantBulkCreate):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    # Find the attributes assigned to products with variant = True
    assignments = db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product_id,
        ProductAttribute.is_variant_attribute.is_(True)
    ).all()
        
    required_attribute_ids = {
        assignment.attribute_id for assignment in assignments
    }

    # Track duplicate skus and combinations in this request
    request_skus = set()
    request_combinations = set()
    new_variants = []

    # Fetch existing SKUs and variant combinations.
    existing_variants = db.query(ProductVariant).filter(
        ProductVariant.product_id == product_id
    ).all()

    existing_combinations = {
        tuple(sorted(value.id
        for value in variant.attribute_values))
        for variant in existing_variants
    }

    for item in variant_data.variants:
        # validate item skus are unique
        if item.sku in request_skus:
            return "duplicate_sku"

        request_skus.add(item.sku)

        # validate sku uniqueness in the database
        sku_exists = db.query(ProductVariant).filter(
            ProductVariant.sku == item.sku
        ).first()

        if sku_exists:
            return "sku_exists"

        # Reject repeated attribute values ids in a single variant i.e [1,1]
        if len(item.attribute_value_ids) != len(set(item.attribute_value_ids)):
            return "duplicate_attribute_values"

        # Fetch and validate the selected values
        values = (
            db.query(AttributeValue)
            .filter(AttributeValue.id.in_(item.attribute_value_ids)).all()
            if item.attribute_value_ids
            else []
        )

        if len(values) != len(item.attribute_value_ids):
            return "attribute_value_not_found"

        selected_attribute_ids = [
            value.attribute_id for value in values
        ]

        if len(selected_attribute_ids) != len(
            set(selected_attribute_ids)
        ):
            return "duplicate_attributes"

        # check if all the assigned attributes are selected or not
        if set(selected_attribute_ids) != required_attribute_ids:
            return "missing_attribute_from_request"

        # prevent duplicate combinations in the request
        combination = tuple(
            sorted(item.attribute_value_ids)
        )

        if combination in request_combinations:
            return "duplicate_combination"

        if combination in existing_combinations:
            return "combination_exists"

        request_combinations.add(combination)

        variant = ProductVariant(
            product_id=product_id,
            sku=item.sku,
            price=item.price,
            stock=item.stock,
            attribute_values=values
        )

        new_variants.append(variant)

    try:
        db.add_all(new_variants)
        db.commit()

        for variant in new_variants:
            db.refresh(variant)

        return new_variants

    except IntegrityError:
        db.rollback()
        return "conflict"

# Fetch product variants with attributes
def fetch_product_variants_by_id(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    variants = (
        db.query(ProductVariant).filter(ProductVariant.product_id == product_id).all()
    )

    return variants