import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Integer, DateTime, Boolean, ForeignKey
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    business_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    soundbox_device_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    soundbox_online: Mapped[bool] = mapped_column(Boolean, default=True)
    health_score: Mapped[int] = mapped_column(Integer, default=88)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    transactions = relationship("Transaction", back_populates="merchant", cascade="all, delete-orphan")
    khata_entries = relationship("KhataEntry", back_populates="merchant", cascade="all, delete-orphan")
    loans = relationship("LoanApplication", back_populates="merchant", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(50), ForeignKey("merchants.id"), index=True, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(20), default="Paytm UPI")
    payer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="SUCCESS")
    chime_played: Mapped[bool] = mapped_column(Boolean, default=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    is_split_settlement: Mapped[bool] = mapped_column(Boolean, default=False)
    settled_khata_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    settled_khata_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    net_sale_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    soundbox_chime_text: Mapped[str | None] = mapped_column(String(255), nullable=True)

    merchant = relationship("Merchant", back_populates="transactions")

class KhataEntry(Base):
    __tablename__ = "khata_entries"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(50), ForeignKey("merchants.id"), index=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(15), nullable=False)
    customer_vpa: Mapped[str | None] = mapped_column(String(80), nullable=True)
    amount_due: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    due_date: Mapped[str] = mapped_column(String(20), nullable=False)
    days_overdue: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING, CRITICAL, REMINDED, SETTLED
    source_channel: Mapped[str] = mapped_column(String(30), default="COUNTER_QR_WEB")
    settled_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    settled_by_txn_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_reminder_sent: Mapped[str | None] = mapped_column(String(50), nullable=True)

    merchant = relationship("Merchant", back_populates="khata_entries")

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(50), ForeignKey("merchants.id"), index=True, nullable=False)
    pre_approved_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=50000.00)
    daily_sweep_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=300.00)
    interest_rate_pct: Mapped[float] = mapped_column(Numeric(4, 2), default=1.25)
    tenure_days: Mapped[int] = mapped_column(Integer, default=180)
    bank_account_mask: Mapped[str] = mapped_column(String(60), default="Paytm Payments Bank **********4821")
    status: Mapped[str] = mapped_column(String(25), default="OFFERED")  # OFFERED, CLAIMED, DISBURSED
    claimed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="loans")

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
