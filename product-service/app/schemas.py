from pydantic import BaseModel, ConfigDict

class CategoryCreate(BaseModel):
    name: str
    description: str | None = None

class CategoryResponse(CategoryCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)