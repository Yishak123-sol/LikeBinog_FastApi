from fastapi import File, UploadFile
from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from typing import Any
from app.models import Role

from pydantic import BaseModel, Field
from typing import List, Dict


class UserUpdate(BaseModel):
    id: int
    phone: Optional[str] = None
    region: Optional[str] = None
    profile_picture: Optional[str] = None
    parent_id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None
    remaining_balance: Optional[float] = None
    role: Optional[str] = None
    password: Optional[str] = None
    created_by: Optional[int] = None


class BingoCardFetch(BaseModel):
    bingo_card_code: str


class BingoCardCreate(BaseModel):
    B: List[int]
    I: List[int]
    N: List[int]
    G: List[int]
    O: List[int]
    cardNumber: List[int]


class MultipleBingoCardsCreate(BaseModel):
    cards: List[BingoCardCreate]
    id: int


class UserLogin(BaseModel):
    phone: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class GameTransactionModel(BaseModel):
    bet_amount: int
    game_type: str
    number_of_cards: int
    dedacted_amount: int


class PackageTransactionModel(BaseModel):
    package_amount: float


class BingoCardOut(BaseModel):
    id: int
    owner_id: int | None
    card_data: Any
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    phone: str
    region: Optional[str] = None
    remaining_balance: Optional[float] = None
    profile_picture: Optional[str] = None
    parent_id: Optional[int] = None
    id: int
    name: Optional[str] = None
    city: Optional[str] = None
    role: str
    total_balance: Optional[float] = None
    created_by: Optional[int] = None
    created_at: datetime
    bingo_card_code: Optional[str] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenData(BaseModel):
    id: Optional[int] = None


class UserCreate(BaseModel):
    phone: str
    remaining_balance: Optional[float] = 0.0
    name: Optional[str] = None
    role: Role
    city: Optional[str] = None
    region: Optional[str] = None
    password: str
    profile_picture: Optional[str] = None
    parent_id: Optional[int] = None
