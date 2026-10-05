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
    product_id: int
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