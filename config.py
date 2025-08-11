import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # Bot tokens
    MAIN_BOT_TOKEN: str = os.getenv("MAIN_BOT_TOKEN", "")
    ADMIN_BOT_TOKEN: str = os.getenv("ADMIN_BOT_TOKEN", "")
    
    # Admin credentials
    ADMIN_TELEGRAM_ID: int = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///rental_bot.db")
    
    # Payment configuration
    PAYMENT_CARD_NUMBER: str = "9860350140898858"
    PAYMENT_RECIPIENT: str = "BEKCHANOV B."
    ADMIN_TELEGRAM_USERNAME: str = "@MrLogon1221"
    
    # Subscription prices
    MONTHLY_SUBSCRIPTION_PRICE: int = 12000  # som
    YEARLY_SUBSCRIPTION_PRICE: int = 100000  # som
    
    # Free property limit
    FREE_PROPERTY_LIMIT: int = 1
    
    # Notification settings
    RENT_REMINDER_DAYS: int = 3  # Days before rent due date to send reminder
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        config = cls()
        if not config.MAIN_BOT_TOKEN:
            raise ValueError("MAIN_BOT_TOKEN is required")
        if not config.ADMIN_BOT_TOKEN:
            raise ValueError("ADMIN_BOT_TOKEN is required")
        if not config.ADMIN_TELEGRAM_ID:
            raise ValueError("ADMIN_TELEGRAM_ID is required")
        return True

# Global config instance
config = Config()
