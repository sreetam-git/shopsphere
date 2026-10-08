from fastapi import APIRouter, status, Depends, HTTPException
from ..database import get_db
from ..schemas import (AttributeCreate, 
                       AttributeResponse, 
                       AttributeValueCreate, 
                       AttributeValueResponse,
                       )
from ..crud import (
    create_attribute, 
    fetch_attributes, 
    get_attribute_by_id, 
    create_attribute_value, 
    get_attribute_values_by_id)

from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/attributes",
    tags=["Attributes"]
)

@router.post("/", response_model=AttributeResponse)
def add_attribute(attribute_data: AttributeCreate, db: Session = Depends(get_db)):
    result = create_attribute(db, attribute_data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attribute already exists"
        )
    return result

@router.get("/", response_model=list[AttributeResponse])
def get_attributes(db: Session = Depends(get_db)):
    result = fetch_attributes(db)
    return result

@router.get("/{attribute_id}", response_model=AttributeResponse)
def get_attribute_details(attribute_id: int, db: Session = Depends(get_db)):
    result = get_attribute_by_id(db=db, attribute_id=attribute_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attribute id does not exist"
        )

    return result

@router.post("/{attribute_id}/values", response_model=AttributeValueResponse)
def add_attribute_value(attribute_id: int, values_data: AttributeValueCreate, db: Session = Depends(get_db)):
    result = create_attribute_value(db=db, attribute_id=attribute_id, value_data=values_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute does not exist"
        )

    if result == "value_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attribute value already exists"
        )

    return result

@router.get("/{attribute_id}/values", response_model=list[AttributeValueResponse], status_code=status.HTTP_200_OK)
def get_attribute_values(attribute_id: int, db: Session = Depends(get_db)):
    result = get_attribute_values_by_id(db, attribute_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attribute does not exist"
        )

    return result