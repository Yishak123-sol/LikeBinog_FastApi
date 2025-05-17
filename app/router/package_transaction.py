from fastapi import APIRouter, Depends, HTTPException, status
from .. import models, oauth2, schemas
from sqlalchemy.orm import Session
from .. import database, models
from sqlalchemy import or_

router = APIRouter(tags=["Package Transaction"], prefix="/package")


@router.post("/{given_receiver_id}", status_code=status.HTTP_201_CREATED)
def create_package_transaction(
    given_receiver_id: int,
    package_transaction: schemas.PackageTransactionModel,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    receiver_user = (
        db.query(models.User).filter(models.User.id == given_receiver_id).first()
    )
    if not receiver_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Receiver user not found",
        )

    if current_user.role.value == "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This user role does not have permission to transfer pakcage",
        )

    if (
        current_user.remaining_balance < package_transaction.package_amount
        and current_user.role.value != "owner"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient balance",
        )

    if current_user.id == given_receiver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You cannot transfer to yourself",
        )

    sender_name = (
        db.query(models.User).filter(models.User.id == current_user.id).first().name
    )
    receiver_name = (
        db.query(models.User).filter(models.User.id == given_receiver_id).first().name
    )

    updated_sender_package_amount = (
        current_user.remaining_balance - package_transaction.package_amount
    )

    updated_receiver_package_amount = (
        db.query(models.User)
        .filter(models.User.id == given_receiver_id)
        .first()
        .remaining_balance
        + package_transaction.package_amount
    )

    total_balance = (
        db.query(models.User)
        .filter(models.User.id == given_receiver_id)
        .first()
        .total_balance
        + package_transaction.package_amount
    )

    db.query(models.User).filter(models.User.id == current_user.id).update(
        {
            "total_balance": total_balance,
        }
    )

    db.query(models.User).filter(models.User.id == current_user.id).update(
        {
            "remaining_balance": updated_sender_package_amount,
        }
    )
    db.query(models.User).filter(models.User.id == given_receiver_id).update(
        {
            "remaining_balance": updated_receiver_package_amount,
        }
    )

    db.commit()

    new_package_transaction = models.PackageTransaction(
        receiver_id=given_receiver_id,
        sender_id=current_user.id,
        receiver_name=receiver_name,
        sender_name=sender_name,
        **package_transaction.dict(),
    )

    # update user total and remaining balance
    db.add(new_package_transaction)
    db.commit()
    db.refresh(new_package_transaction)

    return {
        "message": "Pakcage Transaction Created Successfully",
        "package_transaction": new_package_transaction,
    }


# @router.post("/owner/{given_receiver_id}", status_code=status.HTTP_201_CREATED)
# def create_package_transaction(
#     given_receiver_id: int,
#     package_transaction: schemas.PackageTransactionModel,
#     db: Session = Depends(database.get_db),
#     current_user: int = Depends(oauth2.get_current_user),
# ):

#     if not current_user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     receiver_user = (
#         db.query(models.User).filter(models.User.id == given_receiver_id).first()
#     )
#     if not receiver_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Receiver user not found",
#         )

#     if current_user.role.value != "owner":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=f"This user role does not have permission to transfer pakcage",
#         )

#     if current_user.id == given_receiver_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=f"You cannot transfer to yourself",
#         )

#     sender_name = (
#         db.query(models.User).filter(models.User.id == current_user.id).first().name
#     )
#     receiver_name = (
#         db.query(models.User).filter(models.User.id == given_receiver_id).first().name
#     )

#     updated_receiver_package_amount = (
#         db.query(models.User)
#         .filter(models.User.id == given_receiver_id)
#         .first()
#         .remaining_balance
#         + package_transaction.package_amount
#     )

#     db.query(models.User).filter(models.User.id == given_receiver_id).update(
#         {
#             "remaining_balance": updated_receiver_package_amount,
#         }
#     )
#     db.commit()

#     new_package_transaction = models.PackageTransaction(
#         receiver_id=given_receiver_id,
#         sender_id=current_user.id,
#         receiver_name=receiver_name,
#         sender_name=sender_name,
#         **package_transaction.dict(),
#     )

#     # update user total and remaining balance
#     db.add(new_package_transaction)
#     db.commit()
#     db.refresh(new_package_transaction)

#     return {
#         "message": "Pakcage Transaction Created Successfully",
#         "package_transaction": new_package_transaction,
#     }


@router.get("/")
def get_package_transactions(
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

    package_transaction = db.query(models.PackageTransaction).all()
    if not package_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No package transaction found",
        )

    return package_transaction


@router.get("/my-package-transaction")
def get_package_transaction_by_userid(
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    package_transaction = (
        db.query(models.PackageTransaction)
        .filter(
            or_(
                models.PackageTransaction.receiver_id == current_user.id,
                models.PackageTransaction.sender_id == current_user.id,
            )
        )
        .all()
    )
    if not package_transaction:
        raise HTTPException(
            status_code=404, detail="you don't have a package transaction yet."
        )

    return package_transaction


@router.get("/my/{id}")
def get_package_transaction_by_userid(
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

    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )

    package_transaction = db.query(models.PackageTransaction).all()

    if not package_transaction:
        raise HTTPException(
            status_code=404, detail="There is no package transaction yet."
        )

    if user.role.value == "owner":
        return package_transaction

    package_transactions = (
        db.query(models.PackageTransaction)
        .filter(
            or_(
                models.PackageTransaction.receiver_id == id,
                models.PackageTransaction.sender_id == id,
            )
        )
        .all()
    )
    if not package_transactions:
        raise HTTPException(
            status_code=404, detail="you don't have a package transaction yet."
        )

    return package_transactions
