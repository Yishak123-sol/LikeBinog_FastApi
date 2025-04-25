from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, oauth2, helper
from app.database import get_db
from app.schemas import MultipleBingoCardsCreate
from .. import schemas

router = APIRouter(prefix="/cards", tags=["Bingo Cards"])


@router.post("/")
def get_bingo_cards_byId(
    bingo_card: schemas.BingoCardFetch, db: Session = Depends(get_db)
):

    bingo_cards = (
        db.query(models.BingoCard)
        .filter((models.BingoCard.id == bingo_card.bingo_card_code))
        .first()
    )

    if not bingo_cards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bingo card not found",
        )

    return bingo_cards


@router.post("/bingo_cards/")
def create_bingo_cards(
    bingo_cards: MultipleBingoCardsCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    id = bingo_cards.id
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )
    card = db.query(models.BingoCard).filter(models.BingoCard.owner_id == id).first()
    if card:
        db.delete(card)
        db.commit()

    created_cards = []
    for card in bingo_cards.cards:
        card_dict = {
            "B": card.B,
            "I": card.I,
            "N": card.N,
            "G": card.G,
            "O": card.O,
            "cardNumber": card.cardNumber,
        }
        created_cards.append(card_dict)

    card_dict = {
        "cards": created_cards,
    }
    card_id = helper.generate_unique_code(db)
    db_card = models.BingoCard(owner_id=id, card_data=card_dict, id=card_id)
    user = db.query(models.User).filter(models.User.id == id).first()

    db.add(db_card)
    db.commit()
    db.query(models.User).filter(models.User.id == id).update(
        {
            "bingo_card_code": card_id,
        }
    )
    db.commit()

    db.refresh(db_card)

    return created_cards
