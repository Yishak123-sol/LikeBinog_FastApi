from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import database
from .. import models, utils, oauth2, schemas


router = APIRouter(tags=["Authentication"])


@router.post(
    "/login", status_code=status.HTTP_201_CREATED, response_model=schemas.LoginResponse
)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(models.User)
        .filter(
            models.User.phone == user_credentials.username,
        )
        .first()
    )

    if not user:
        print("User not found")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid Credentials",
        )

    if not utils.verify_password(user_credentials.password, user.password):
        print("Invalid password")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials"
        )

    # creat token
    access_token = oauth2.create_access_token(
        data={"user_id": user.id, "role": user.role.value}
    )

    # return token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
