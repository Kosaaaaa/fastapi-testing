from __future__ import annotations

from collections.abc import Generator

import fastapi
from pydantic import BaseModel
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Item(BaseModel):
    id: int
    name: str
    description: str | None


class ItemCreate(BaseModel):
    name: str
    description: str | None


class ItemUpdate(BaseModel):
    name: str | None
    description: str | None


DATABASE_URL = "sqlite:///test.db"


class Base(DeclarativeBase):
    pass


class DBItem(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str | None]


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = fastapi.FastAPI()


# Dependency to get the database session
def get_db() -> Generator[Session, None, None]:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


@app.on_event("startup")
async def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.post("/items")
def create_item(item: ItemCreate, db: Session = fastapi.Depends(get_db)) -> Item:
    db_item = DBItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return Item(**db_item.__dict__)


@app.get("/items")
def read_items(db: Session = fastapi.Depends(get_db)) -> list[Item]:
    db_items = db.query(DBItem).all()
    return [Item(**db_item.__dict__) for db_item in db_items]


@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = fastapi.Depends(get_db)) -> Item:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    return Item(**db_item.__dict__)


@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemUpdate, db: Session = fastapi.Depends(get_db)) -> Item:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return Item(**db_item.__dict__)


@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = fastapi.Depends(get_db)) -> Item:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return Item(**db_item.__dict__)
