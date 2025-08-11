from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio
from config import config
from database.models import Base

# Convert sync DATABASE_URL to async if needed
database_url = config.DATABASE_URL
if database_url.startswith("sqlite://"):
    async_database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")
elif database_url.startswith("postgresql://"):
    async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    # Remove sslmode parameter if present for asyncpg
    if "sslmode=" in async_database_url:
        import re
        async_database_url = re.sub(r'[?&]sslmode=[^&]*', '', async_database_url)
        async_database_url = re.sub(r'\?$', '', async_database_url)
else:
    async_database_url = database_url

# Create async engine with connection pooling
engine = create_async_engine(
    async_database_url, 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"server_settings": {"jit": "off"}} if "postgresql" in async_database_url else {}
)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with error handling"""
    session = None
    try:
        session = async_session_maker()
        yield session
        await session.commit()
    except Exception as e:
        if session:
            await session.rollback()
        print(f"Database session error: {e}")
        raise
    finally:
        if session:
            await session.close()

async def init_database():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # Tables might already exist, which is fine
        print(f"Database tables already exist or initialization skipped: {e}")

# Database service functions
from database.models import User, Property, Tenant, Subscription, PremiumRequest, AdminSession, AdminConfig
from sqlalchemy import select, update, delete
from datetime import datetime, timedelta

class DatabaseService:
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> User:
        """Get user by telegram ID"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> User:
        """Get user by ID"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(telegram_id: int, language: str = "uz") -> User:
        """Create new user"""
        async with get_session() as session:
            user = User(telegram_id=telegram_id, language=language)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    @staticmethod
    async def update_user(telegram_id: int = None, user_id: int = None, **kwargs) -> User:
        """Update user information"""
        async with get_session() as session:
            if telegram_id:
                await session.execute(
                    update(User).where(User.telegram_id == telegram_id).values(**kwargs)
                )
                await session.commit()
                return await DatabaseService.get_user_by_telegram_id(telegram_id)
            elif user_id:
                await session.execute(
                    update(User).where(User.id == user_id).values(**kwargs)
                )
                await session.commit()
                # Get user by ID
                result = await session.execute(select(User).where(User.id == user_id))
                return result.scalar_one()
            else:
                raise ValueError("Either telegram_id or user_id must be provided")
    
    @staticmethod
    async def get_user_properties(user_id: int) -> list[Property]:
        """Get all properties for a user"""
        async with get_session() as session:
            result = await session.execute(
                select(Property).where(Property.owner_id == user_id)
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def create_property(owner_id: int, address: str, area_sqm: float, 
                            rooms_count: int, monthly_rent: float, currency: str = "UZS") -> Property:
        """Create new property"""
        async with get_session() as session:
            property_obj = Property(
                owner_id=owner_id,
                address=address,
                area_sqm=area_sqm,
                rooms_count=rooms_count,
                monthly_rent=monthly_rent,
                currency=currency
            )
            session.add(property_obj)
            await session.commit()
            await session.refresh(property_obj)
            return property_obj
    
    @staticmethod
    async def get_user_tenants(user_id: int) -> list[Tenant]:
        """Get all tenants for a user"""
        async with get_session() as session:
            result = await session.execute(
                select(Tenant).where(Tenant.landlord_id == user_id)
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def create_tenant(landlord_id: int, property_id: int, full_name: str,
                          passport_series: str, passport_number: str, 
                          move_in_date: datetime, rent_due_date: int) -> Tenant:
        """Create new tenant"""
        async with get_session() as session:
            # Get property rent amount
            property_result = await session.execute(
                select(Property).where(Property.id == property_id)
            )
            property_obj = property_result.scalar_one()
            
            tenant = Tenant(
                landlord_id=landlord_id,
                property_id=property_id,
                full_name=full_name,
                passport_series=passport_series,
                passport_number=passport_number,
                move_in_date=move_in_date,
                rent_due_date=rent_due_date,
                amount_due=property_obj.monthly_rent
            )
            session.add(tenant)
            await session.commit()
            await session.refresh(tenant)
            return tenant
    
    @staticmethod
    async def create_premium_request(user_id: int, subscription_type: str, amount: float) -> PremiumRequest:
        """Create premium request"""
        async with get_session() as session:
            request = PremiumRequest(
                user_id=user_id,
                subscription_type=subscription_type,
                amount=amount
            )
            session.add(request)
            await session.commit()
            await session.refresh(request)
            return request
    
    @staticmethod
    async def get_pending_premium_requests() -> list[PremiumRequest]:
        """Get all pending premium requests"""
        async with get_session() as session:
            result = await session.execute(
                select(PremiumRequest).where(PremiumRequest.status == "pending")
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def approve_premium_request(request_id: int) -> bool:
        """Approve premium request and activate user premium"""
        async with get_session() as session:
            # Get the request
            request_result = await session.execute(
                select(PremiumRequest).where(PremiumRequest.id == request_id)
            )
            request = request_result.scalar_one_or_none()
            
            if not request:
                return False
            
            # Update request status
            await session.execute(
                update(PremiumRequest)
                .where(PremiumRequest.id == request_id)
                .values(status="approved", processed_at=datetime.utcnow())
            )
            
            # Calculate premium expiry
            if request.subscription_type == "monthly":
                expires_at = datetime.utcnow() + timedelta(days=30)
            else:  # yearly
                expires_at = datetime.utcnow() + timedelta(days=365)
            
            # Update user premium status
            await session.execute(
                update(User)
                .where(User.id == request.user_id)
                .values(is_premium=True, premium_expires_at=expires_at)
            )
            
            await session.commit()
            return True
    
    @staticmethod
    async def get_all_users() -> list[User]:
        """Get all users"""
        async with get_session() as session:
            result = await session.execute(select(User))
            return list(result.scalars().all())
    
    @staticmethod
    async def get_user_stats() -> dict:
        """Get user statistics"""
        async with get_session() as session:
            # Total users
            total_result = await session.execute(select(User))
            total_users = len(total_result.scalars().all())
            
            # Premium users
            premium_result = await session.execute(
                select(User).where(User.is_premium == True)
            )
            premium_users = len(premium_result.scalars().all())
            
            # Recent users (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_result = await session.execute(
                select(User).where(User.created_at >= week_ago)
            )
            recent_users = len(recent_result.scalars().all())
            
            return {
                "total_users": total_users,
                "premium_users": premium_users,
                "recent_users": recent_users
            }
    
    @staticmethod
    async def authenticate_admin(telegram_id: int) -> bool:
        """Check if admin is authenticated"""
        async with get_session() as session:
            result = await session.execute(
                select(AdminSession).where(
                    AdminSession.telegram_id == telegram_id,
                    AdminSession.is_authenticated == True
                )
            )
            session_obj = result.scalar_one_or_none()
            
            if session_obj:
                # Update last activity
                await session.execute(
                    update(AdminSession)
                    .where(AdminSession.id == session_obj.id)
                    .values(last_activity=datetime.utcnow())
                )
                await session.commit()
                return True
            return False
    
    @staticmethod
    async def create_admin_session(telegram_id: int) -> None:
        """Create admin session"""
        async with get_session() as session:
            # Remove old sessions
            await session.execute(
                delete(AdminSession).where(AdminSession.telegram_id == telegram_id)
            )
            
            # Create new session
            admin_session = AdminSession(telegram_id=telegram_id, is_authenticated=True)
            session.add(admin_session)
            await session.commit()
    
    @staticmethod
    async def set_admin_config(key: str, value: str) -> None:
        """Set admin configuration value"""
        async with get_session() as session:
            # Check if config exists
            result = await session.execute(
                select(AdminConfig).where(AdminConfig.key == key)
            )
            config_obj = result.scalar_one_or_none()
            
            if config_obj:
                # Update existing
                await session.execute(
                    update(AdminConfig)
                    .where(AdminConfig.key == key)
                    .values(value=value, updated_at=datetime.utcnow())
                )
            else:
                # Create new
                config_obj = AdminConfig(key=key, value=value)
                session.add(config_obj)
            
            await session.commit()
    
    @staticmethod
    async def get_admin_config(key: str, default: str = None) -> str:
        """Get admin configuration value"""
        async with get_session() as session:
            result = await session.execute(
                select(AdminConfig).where(AdminConfig.key == key)
            )
            config_obj = result.scalar_one_or_none()
            
            if config_obj:
                return config_obj.value
            return default
    
    @staticmethod
    async def get_tenants_with_properties(user_id: int) -> list:
        """Get all tenants for a user with property information"""
        async with get_session() as session:
            result = await session.execute(
                select(Tenant, Property)
                .join(Property, Tenant.property_id == Property.id)
                .where(Tenant.landlord_id == user_id)
            )
            return list(result.all())
    
    @staticmethod
    async def update_tenant_payment_status(tenant_id: int, status: str, amount_paid: float = None) -> bool:
        """Update tenant payment status"""
        async with get_session() as session:
            update_values = {
                "payment_status": status,
                "last_payment_date": datetime.utcnow()
            }
            
            if amount_paid is not None:
                update_values["amount_paid"] = amount_paid
            
            await session.execute(
                update(Tenant)
                .where(Tenant.id == tenant_id)
                .values(**update_values)
            )
            await session.commit()
            return True
    
    @staticmethod
    async def get_overdue_tenants() -> list[Tenant]:
        """Get all tenants with overdue payments"""
        async with get_session() as session:
            # Get tenants who haven't paid this month
            current_date = datetime.utcnow()
            result = await session.execute(
                select(Tenant)
                .where(Tenant.payment_status == "overdue")
                .order_by(Tenant.rent_due_date)
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def get_upcoming_rent_due_tenants(days_ahead: int = 3) -> list[Tenant]:
        """Get tenants whose rent is due in specified days"""
        async with get_session() as session:
            current_date = datetime.utcnow()
            target_day = (current_date + timedelta(days=days_ahead)).day
            
            result = await session.execute(
                select(Tenant)
                .where(
                    Tenant.rent_due_date == target_day,
                    Tenant.payment_status.in_(["pending", "partial"])
                )
            )
            return list(result.scalars().all())
