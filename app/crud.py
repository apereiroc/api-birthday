from fastapi import HTTPException
from sqlmodel import select
from app.database import SessionDep
from app.models import UserCreate, User, UserPublic
from app.routers import user_router
import logging

logger = logging.getLogger(__name__)


@user_router.post("/", response_model=UserPublic)
async def create_user_if_not_exists(user: UserCreate, db: SessionDep) -> User:
    logger.debug(f"Received user: {user}")

    logger.info("Searching user in the DB ...")
    existing_user: User | None = db.exec(
        select(User).where(User.telegram_id == user.telegram_id)
    ).first()
    if existing_user:
        logger.error(f"User with name `{user.first_name}` is already registered")
        raise HTTPException(status_code=409, detail="User already exists")

    logger.info("Creating new user ...")
    db_user: User = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
