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


# product <-> attribute association
product_attributes = Table(
    "product_attributes",
    Base.metadata,

    Column(
        "product_id",
        ForeignKey("products.id"),
        primary_key=True
    ),
    Column(
        "attribute_id",
        ForeignKey("attributes.id"),
        primary_key=True
    )
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

    attributes = relationship(
        "Attribute",
        secondary=product_attributes,
        back_populates="products"
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

    products = relationship(
        "Product",
        secondary=product_attributes,
        back_populates="attributes"
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
