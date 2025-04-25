from fastapi import APIRouter, Depends, HTTPException, status
from .. import models, oauth2, schemas
from sqlalchemy.orm import Session
from .. import database, models

router = APIRouter(tags=["Game Transaction"], prefix="/gamet")


# "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozLCJyb2xlIjoibWFuYWdlciIsImV4cCI6MTc0NDE0NDc3Mn0.MRk9JAZPXNKNx_qwvyK7f1yupWO19f5dYY66phSJPwY"
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_game_transaction(
    game_transaction: schemas.GameTransactionModel,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # if current_user.role.value != "user":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail=f"This user role does not have permission to create a game transaction",
    #     )

    remaining_balance = (
        db.query(models.User)
        .filter(models.User.id == current_user.id)
        .first()
        .remaining_balance
    )

    if remaining_balance < game_transaction.dedacted_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You don't have enough balance to place this bet",
        )

    new_game_transaction = models.GameTransaction(
        remaining_balance=remaining_balance - game_transaction.dedacted_amount,
        total_balance=current_user.total_balance,
        owner_id=current_user.id,
        owner_name=current_user.name,
        **game_transaction.dict(),
    )
    db.add(new_game_transaction)
    db.commit()
    db.refresh(new_game_transaction)

    return {
        "message": "Game Transaction Created Successfully",
        "game_transaction": new_game_transaction,
    }


@router.get("/")
def get_game_transactions(
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if current_user.role.value != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"you do not have permission to access this data",
        )

    game_transaction = db.query(models.GameTransaction).all()
    if not game_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No game transaction found",
        )

    return game_transaction


@router.get("/my/{id}")
def get_game_transaction_by_userid(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    game_transaction = (
        db.query(models.GameTransaction)
        .filter(models.GameTransaction.owner_id == id)
        .all()
    )
    if not game_transaction:
        raise HTTPException(
            status_code=404, detail="you don't have a game transaction yet."
        )

    return game_transaction


@router.get("/my-game-transaction")
def get_game_transaction_by_userid(
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    game_transaction = (
        db.query(models.GameTransaction)
        .filter(models.GameTransaction.owner_id == current_user.id)
        .all()
    )
    if not game_transaction:
        raise HTTPException(
            status_code=404, detail="you don't have a game transaction yet."
        )

    return game_transaction
