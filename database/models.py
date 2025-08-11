from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String(255))
    phone_number = Column(String(20))
    language = Column(String(2), default="uz")  # uz or ru
    is_premium = Column(Boolean, default=False)
    premium_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    properties = relationship("Property", back_populates="owner", cascade="all, delete-orphan")
    tenants = relationship("Tenant", back_populates="landlord", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    premium_requests = relationship("PremiumRequest", back_populates="user", cascade="all, delete-orphan")

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address = Column(Text, nullable=False)
    area_sqm = Column(Float, nullable=False)
    rooms_count = Column(Integer, nullable=False)
    monthly_rent = Column(Float, nullable=False)
    currency = Column(String(3), default="UZS")  # UZS or USD
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="properties")
    tenants = relationship("Tenant", back_populates="property", cascade="all, delete-orphan")

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True)
    landlord_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    full_name = Column(String(255), nullable=False)
    passport_series = Column(String(10), nullable=False)
    passport_number = Column(String(20), nullable=False)
    move_in_date = Column(DateTime, nullable=False)
    rent_due_date = Column(Integer, default=1)  # Day of month when rent is due
    last_payment_date = Column(DateTime, nullable=True)
    payment_status = Column(String(20), default="pending")  # pending, paid, partial, overdue
    amount_paid = Column(Float, default=0.0)
    amount_due = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    landlord = relationship("User", back_populates="tenants")
    property = relationship("Property", back_populates="tenants")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_type = Column(String(20), nullable=False)  # monthly, yearly
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50))
    payment_status = Column(String(20), default="pending")  # pending, paid, expired
    starts_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")

class PremiumRequest(Base):
    __tablename__ = "premium_requests"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_type = Column(String(20), nullable=False)  # monthly, yearly
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="premium_requests")

class AdminSession(Base):
    __tablename__ = "admin_sessions"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    is_authenticated = Column(Boolean, default=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class AdminConfig(Base):
    __tablename__ = "admin_config"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
