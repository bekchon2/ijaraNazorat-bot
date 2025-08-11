import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database.database import DatabaseService
from localization.translations import get_text
from config import config

class NotificationService:
    def __init__(self, main_bot, admin_bot):
        self.main_bot = main_bot
        self.admin_bot = admin_bot
        self.scheduler = AsyncIOScheduler()
    
    def start_scheduler(self):
        """Start the notification scheduler"""
        # Check rent reminders daily at 09:00
        self.scheduler.add_job(
            self.send_rent_reminders,
            CronTrigger(hour=9, minute=0),
            id='rent_reminders'
        )
        
        # Check overdue payments daily at 10:00
        self.scheduler.add_job(
            self.send_overdue_notifications,
            CronTrigger(hour=10, minute=0),
            id='overdue_notifications'
        )
        
        self.scheduler.start()
    
    async def send_rent_reminders(self):
        """Send rent payment reminders"""
        try:
            # Get all tenants whose rent is due in X days
            from database.database import get_session
            from database.models import Tenant, User, Property
            from sqlalchemy import select
            
            async with get_session() as session:
                # Calculate target day of month
                today = datetime.now()
                target_date = today + timedelta(days=config.RENT_REMINDER_DAYS)
                target_day = target_date.day
                
                # Get tenants whose rent is due on target day
                result = await session.execute(
                    select(Tenant, User, Property)
                    .join(User, Tenant.landlord_id == User.id)
                    .join(Property, Tenant.property_id == Property.id)
                    .where(Tenant.rent_due_date == target_day)
                    .where(Tenant.payment_status.in_(["pending", "partial"]))
                )
                
                for tenant, user, property_obj in result:
                    message_text = get_text(
                        user.language,
                        "rent_reminder",
                        tenant_name=tenant.full_name,
                        property_address=property_obj.address,
                        days=config.RENT_REMINDER_DAYS
                    )
                    
                    try:
                        await self.main_bot.send_message(
                            user.telegram_id,
                            message_text
                        )
                    except Exception as e:
                        print(f"Failed to send reminder to user {user.telegram_id}: {e}")
        
        except Exception as e:
            print(f"Error in send_rent_reminders: {e}")
    
    async def send_overdue_notifications(self):
        """Send overdue payment notifications"""
        try:
            from database.database import get_session
            from database.models import Tenant, User, Property
            from sqlalchemy import select
            
            async with get_session() as session:
                # Get tenants with overdue payments
                today = datetime.now()
                current_day = today.day
                
                result = await session.execute(
                    select(Tenant, User, Property)
                    .join(User, Tenant.landlord_id == User.id)
                    .join(Property, Tenant.property_id == Property.id)
                    .where(Tenant.rent_due_date < current_day)
                    .where(Tenant.payment_status.in_(["pending", "partial"]))
                )
                
                for tenant, user, property_obj in result:
                    overdue_amount = tenant.amount_due - tenant.amount_paid
                    
                    message_text = get_text(
                        user.language,
                        "rent_overdue",
                        tenant_name=tenant.full_name,
                        property_address=property_obj.address,
                        amount=f"{overdue_amount:,.0f}",
                        currency=property_obj.currency
                    )
                    
                    try:
                        await self.main_bot.send_message(
                            user.telegram_id,
                            message_text
                        )
                    except Exception as e:
                        print(f"Failed to send overdue notification to user {user.telegram_id}: {e}")
        
        except Exception as e:
            print(f"Error in send_overdue_notifications: {e}")
    
    @staticmethod
    async def notify_admin_payment_request(user, subscription_type, amount):
        """Send payment request notification to admin"""
        try:
            from admin_bot import admin_bot
        except ImportError:
            # Admin bot not available in this context
            admin_bot = None
        
        unknown_text = "Noma'lum"
        sub_text = "Oylik" if subscription_type == "monthly" else "Yillik"
        current_time = datetime.now().strftime('%d.%m.%Y %H:%M')
        
        message_text = f"""💎 Yangi premium so'rov!

👤 Foydalanuvchi: {user.full_name or unknown_text}
📞 Telefon: {user.phone_number or unknown_text}
💰 Summa: {amount:,} so'm
📅 Obuna turi: {sub_text}
🕐 Vaqt: {current_time}

Admin paneliga o'ting: /start"""
        
        if admin_bot:
            try:
                await admin_bot.send_message(
                    config.ADMIN_TELEGRAM_ID,
                    message_text
                )
            except Exception as e:
                print(f"Failed to send admin notification: {e}")
        else:
            print("Admin bot not available for notification")
    
    @staticmethod
    async def notify_user_premium_activated(user):
        """Send premium activation notification to user"""
        from main_bot import main_bot
        
        message_text = get_text(user.language, "success") + " ✅ Sizning premium obunangiz faollashtirildi!"
        
        try:
            await main_bot.send_message(
                user.telegram_id,
                message_text
            )
        except Exception as e:
            print(f"Failed to send user notification: {e}")

# Global notification service instance
notification_service = None

def init_notification_service(main_bot, admin_bot):
    """Initialize notification service"""
    global notification_service
    notification_service = NotificationService(main_bot, admin_bot)
    return notification_service
