"""Client Ad Account Tracker - FastAPI backend."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

DATABASE_URL = "sqlite:///./tracker.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

STATUSES = ["not_started", "in_progress", "blocked", "live"]


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    accounts: Mapped[list["Account"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    platform: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(20), default="not_started")
    notes: Mapped[str] = mapped_column(String(1000), default="")
    client: Mapped[Client] = relationship(back_populates="accounts")


Base.metadata.create_all(engine)


# ---- Schemas ----
class AccountIn(BaseModel):
    platform: str
    status: str = "not_started"
    notes: str = ""


class AccountPatch(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class AccountOut(AccountIn):
    id: int
    client_id: int
    model_config = {"from_attributes": True}


class ClientIn(BaseModel):
    name: str


class ClientOut(BaseModel):
    id: int
    name: str
    accounts: list[AccountOut] = []
    model_config = {"from_attributes": True}


# ---- App ----
app = FastAPI(title="Client Ad Account Tracker")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_status(status: Optional[str]):
    if status is not None and status not in STATUSES:
        raise HTTPException(422, f"status must be one of {STATUSES}")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/clients", response_model=list[ClientOut])
def list_clients(db: Session = Depends(get_db)):
    return db.scalars(select(Client).order_by(Client.name)).all()


@app.post("/api/clients", response_model=ClientOut, status_code=201)
def create_client(body: ClientIn, db: Session = Depends(get_db)):
    if not body.name.strip():
        raise HTTPException(422, "name is required")
    client = Client(name=body.name.strip())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@app.delete("/api/clients/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.get(Client, client_id) or _404()
    db.delete(client)
    db.commit()


@app.post("/api/clients/{client_id}/accounts", response_model=AccountOut, status_code=201)
def add_account(client_id: int, body: AccountIn, db: Session = Depends(get_db)):
    db.get(Client, client_id) or _404()
    check_status(body.status)
    account = Account(client_id=client_id, **body.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@app.patch("/api/accounts/{account_id}", response_model=AccountOut)
def update_account(account_id: int, body: AccountPatch, db: Session = Depends(get_db)):
    account = db.get(Account, account_id) or _404()
    check_status(body.status)
    for key, value in body.model_dump(exclude_none=True).items():
        setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account


@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    accounts = db.scalars(select(Account)).all()
    return {s: sum(1 for a in accounts if a.status == s) for s in STATUSES}


def _404():
    raise HTTPException(404, "not found")
