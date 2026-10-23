from sqlalchemy import (
    Integer, 
    String, 
    Text, 
    Boolean, 
    Column, 
    DateTime, 
    func, 
    Numeric, 
    ForeignKey,
    Table,
    UniqueConstraint
    )
from sqlalchemy.orm import relationship
from .database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    products = relationship(
        "Product",
        back_populates="category"
    )

class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        primary_key=True
    )
    attribute_id = Column(
        Integer,
        ForeignKey("attributes.id"),
        primary_key=True
    )
    is_variant_attribute = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0"
    )

    product = relationship(
        "Product",
        back_populates="attribute_assignments"
    )
    attribute = relationship(
        "Attribute",
        back_populates="product_assignments"
    )


# Variant Attribute values association
variant_attribute_values = Table(
    "variant_attribute_values",
    Base.metadata,

    Column(
        "variant_id",
        ForeignKey("product_variants.id"),
        primary_key=True
    ),
    Column(
        "attribute_value_id",
        ForeignKey("attribute_values.id"),
        primary_key=True
    )
)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    category = relationship(
        "Category",
        back_populates="products"
    )

    variants = relationship(
        "ProductVariant",
        back_populates="product"
    )

    attribute_assignments = relationship(
        "ProductAttribute",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    images = relationship(
        "ProductImage",
        back_populates="product"
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sku = Column(String(100), nullable=False, unique=True)
    price = Column(Numeric(10,2), nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    product = relationship(
        "Product",
        back_populates="variants"
    )

    attribute_values = relationship(
        "AttributeValue",
        secondary=variant_attribute_values,
        back_populates="variants"
    )

    images = relationship(
        "ProductImage",
        back_populates="variant"
    )

# Attribute
class Attribute(Base):
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    values = relationship(
        "AttributeValue",
        back_populates="attribute",
        cascade="all, delete-orphan"
    )

    product_assignments = relationship(
        "ProductAttribute",
        back_populates="attribute"
    )


# Attribute values
class AttributeValue(Base):
    __tablename__ = "attribute_values"

    id = Column(Integer, primary_key=True, index=True)
    attribute_id = Column(Integer, ForeignKey("attributes.id"), nullable=False)
    value = Column(String(100), nullable=False)

    attribute = relationship(
        "Attribute",
        back_populates="values"
    )

    variants = relationship(
        "ProductVariant",
        secondary=variant_attribute_values,
        back_populates="attribute_values"
    )

    __table_args__ = (
        UniqueConstraint(
            "attribute_id",
            "value",
            name="uq_attribute_value"
        ),
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    # NULL means this is a general product image.
    # A value means the image belongs to a specific variant.
    variant_id = Column(
        Integer,
        ForeignKey("product_variants.id"),
        nullable=True,
        index=True
    )

    storage_key = Column(
        String(500),
        nullable=False,
        unique=True
    )

    alt_text = Column(String(255), nullable=True)

    is_primary = Column(
        Boolean,
        default=False,
        server_default="0",
        nullable=False
    )

    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    product = relationship(
        "Product",
        back_populates="images"
    )

    variant = relationship(
        "ProductVariant",
        back_populates="images"
    )
