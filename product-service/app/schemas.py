from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal

class CategoryCreate(BaseModel):
    name: str
    description: str | None = None

class CategoryResponse(CategoryCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    category_id: int

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    name: str
    description: str | None = None
    category_id: int

class ProductVariantCreate(BaseModel):
    sku: str
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)

class ProductVariantResponse(BaseModel):
    id: int
    product_id: int
    sku: str
    price: Decimal
    stock: int = 0
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class AttributeCreate(BaseModel):
    name: str

class AttributeResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class AttributeValueCreate(BaseModel):
    value: str

class AttributeValueResponse(BaseModel):
    id: int
    attribute_id: int
    value: str

    model_config = ConfigDict(from_attributes=True)

class ProductAttributeAssign(BaseModel):
    attribute_id: int
    is_variant_attribute: bool = False

class ProductAttributeResponse(BaseModel):
    id: int
    name: str
    is_variant_attribute: bool
    
    model_config = ConfigDict(from_attributes=True)

class VariantOptionValueResponse(BaseModel):
    id: int
    value: str

    model_config = ConfigDict(from_attributes=True)

class VariantOptionResponse(BaseModel):
    id: int
    name: str
    values: list[VariantOptionValueResponse]

    model_config = ConfigDict(from_attributes=True)

class ProductVariantItemCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    attribute_value_ids: list[int] = Field(default_factory=list)

class ProductVariantBulkCreate(BaseModel):
    variants: list[ProductVariantItemCreate] = Field(min_length=1)


class VariantAttributeValueResponse(BaseModel):
    id: int
    attribute_id: int
    value: str

    model_config = ConfigDict(from_attributes=True)


class ProductVariantDetailResponse(BaseModel):
    id: int
    product_id: int
    sku: str
    price: Decimal
    stock: int
    is_active: bool
    attribute_values: list[VariantAttributeValueResponse]

    model_config = ConfigDict(from_attributes=True)

class ProductVariantUpdate(BaseModel):
    price: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0, alias="qty")
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")

class ProductImageResponse(BaseModel):
    id: int
    product_id: int
    variant_id: int | None
    storage_key: str
    alt_text: str | None
    is_primary: bool
    display_order: int

    model_config = ConfigDict(from_attributes=True)