from datetime import datetime, timedelta
from database.database import DatabaseService
from database.models import Subscription
from config import config

class PaymentService:
    @staticmethod
    async def create_subscription(user_id: int, subscription_type: str, amount: float) -> Subscription:
        """Create a new subscription"""
        from database.database import get_session
        from database.models import Subscription
        
        # Calculate subscription period
        if subscription_type == "monthly":
            expires_at = datetime.utcnow() + timedelta(days=30)
        else:  # yearly
            expires_at = datetime.utcnow() + timedelta(days=365)
        
        async with get_session() as session:
            subscription = Subscription(
                user_id=user_id,
                subscription_type=subscription_type,
                amount=amount,
                payment_status="paid",
                starts_at=datetime.utcnow(),
                expires_at=expires_at
            )
            session.add(subscription)
            await session.commit()
            await session.refresh(subscription)
            return subscription
    
    @staticmethod
    async def activate_premium(user_id: int, subscription_type: str) -> bool:
        """Activate premium for user"""
        try:
            # Calculate expiry date
            if subscription_type == "monthly":
                expires_at = datetime.utcnow() + timedelta(days=30)
            else:  # yearly
                expires_at = datetime.utcnow() + timedelta(days=365)
            
            # Update user premium status
            from database.database import get_session
            from database.models import User
            from sqlalchemy import update
            
            async with get_session() as session:
                await session.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(is_premium=True, premium_expires_at=expires_at)
                )
                await session.commit()
            
            return True
        except Exception as e:
            print(f"Error activating premium: {e}")
            return False
    
    @staticmethod
    def get_subscription_price(subscription_type: str) -> float:
        """Get subscription price"""
        if subscription_type == "monthly":
            return config.MONTHLY_SUBSCRIPTION_PRICE
        else:  # yearly
            return config.YEARLY_SUBSCRIPTION_PRICE
    
    @staticmethod
    def format_payment_info(language: str) -> str:
        """Format payment information"""
        from localization.translations import get_text
        
        base_info = get_text(language, "payment_info")
        return f"{base_info}\n\n🏪 To'lov qilingandan so'ng '{get_text(language, 'payment_made')}' tugmasini bosing."
