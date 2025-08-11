import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.database import init_database
from handlers import main_handlers, property_handlers, tenant_handlers, subscription_handlers, report_handlers
from services.notification_service import init_notification_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global bot instance
main_bot = None

async def main():
    """Main function to run the bot"""
    global main_bot
    
    # Validate configuration
    config.validate()
    
    # Initialize database
    await init_database()
    logger.info("Database initialized")
    
    # Create bot instance
    main_bot = Bot(
        token=config.MAIN_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Create dispatcher
    dp = Dispatcher()
    
    # Register handlers
    dp.include_router(main_handlers.router)
    dp.include_router(property_handlers.router)
    dp.include_router(tenant_handlers.router)
    dp.include_router(subscription_handlers.router)
    dp.include_router(report_handlers.router)
    
    logger.info("Handlers registered")
    
    # Initialize notification service (will be completed when admin bot is ready)
    try:
        from admin_bot import admin_bot
        notification_service = init_notification_service(main_bot, admin_bot)
        notification_service.start_scheduler()
        logger.info("Notification service started")
    except Exception as e:
        logger.warning(f"Could not initialize notification service: {e}")
    
    try:
        logger.info("Starting IjaraNazorat bot...")
        await dp.start_polling(main_bot)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        await main_bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
