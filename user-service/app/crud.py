from sqlalchemy.orm import Session

from .models import User
from .schemas import UserCreate
from .security import hash_password, verify_password

def create_user(db: Session, user: UserCreate):
    db_user = User(
        name = user.name,
        email = user.email,
        password = hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user