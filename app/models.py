from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SAEnum
from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
import enum
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION


class Role(enum.Enum):
    manager = "manager"
    superagent = "superagent"
    owner = "owner"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)  # Made nullable
    phone = Column(String, unique=True, index=True, nullable=False)  # Required
    password = Column(String, index=True, nullable=False)  # Required
    city = Column(String, index=True, nullable=True)  # Made nullable
    region = Column(String, index=True, nullable=True)  # Made nullable
    role = Column(SAEnum(Role), index=True, nullable=False)  # Required
    remaining_balance = Column(DOUBLE_PRECISION, index=True, nullable=False)
    total_balance = Column(DOUBLE_PRECISION, index=True, nullable=False)
    profile_picture = Column(String, nullable=True)  # Made nullable
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    bingo_card_code = Column(
        String(6), ForeignKey("bingo_cards.id", ondelete="CASCADE"), nullable=True
    )
    parent_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
    )


class GameTransaction(Base):
    __tablename__ = "game_transactions"

    id = Column(Integer, primary_key=True, index=True)
    bet_amount = Column(Integer, index=True)
    game_type = Column(String, index=True)
    number_of_cards = Column(Integer, index=True)
    dedacted_amount = Column(Integer, index=True)
    remaining_balance = Column(DOUBLE_PRECISION, index=True, nullable=False)
    total_balance = Column(DOUBLE_PRECISION, index=True, nullable=False)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner_name = Column(String, index=True)

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class PackageTransaction(Base):
    __tablename__ = "package_transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receiver_name = Column(String, index=True)
    sender_name = Column(String, index=True)
    package_amount = Column(Integer, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class BingoCard(Base):
    __tablename__ = "bingo_cards"
    id = Column(String(6), primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_data = Column(JSONB, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
