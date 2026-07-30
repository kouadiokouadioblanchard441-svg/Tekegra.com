from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean,
    DateTime, Text, JSON, Float, ForeignKey
)
from sqlalchemy.orm import relationship
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="fr")
    is_premium = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    # "pending" | "approved" | "rejected"
    # server_default="approved" so existing DB rows stay approved after migration
    approval_status = Column(String(20), default="pending", server_default="approved", nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    # Registration on 1WIN (user confirmed they signed up with affiliate link)
    has_registered = Column(Boolean, default=False, server_default="false")

    # Counters
    total_analyses = Column(Integer, default=0)
    free_signals_used_today = Column(Integer, default=0)   # conservé (ne plus utiliser)
    last_signal_date = Column(String(20), nullable=True)   # conservé (ne plus utiliser)
    free_signals_used_total = Column(Integer, default=0)   # total à vie

    history = relationship("SignalHistory", back_populates="user")
    premium_info = relationship("PremiumSubscription", back_populates="user", uselist=False)


class PremiumSubscription(Base):
    __tablename__ = "premium_subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    payment_method = Column(String(100), nullable=True)
    amount = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="premium_info")


class SignalHistory(Base):
    __tablename__ = "signal_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    game_type = Column(String(50), nullable=False)  # "luckyjet" or "mines"
    signal_data = Column(JSON, nullable=False)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="history")


class BotSettings(Base):
    __tablename__ = "bot_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(Text, nullable=False)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    admin_id = Column(BigInteger, nullable=False)


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True)
    action = Column(String(255), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
