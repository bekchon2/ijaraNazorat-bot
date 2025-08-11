import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.database import init_database
from handlers import admin_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global bot instance
admin_bot = None

async def main():
    """Main function to run the admin bot"""
    global admin_bot
    
    # Validate configuration
    config.validate()
    
    # Initialize database (shared with main bot)
    await init_database()
    logger.info("Database initialized for admin bot")
    
    # Create bot instance
    admin_bot = Bot(
        token=config.ADMIN_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Create dispatcher
    dp = Dispatcher()
    
    # Register admin handlers
    dp.include_router(admin_handlers.router)
    
    logger.info("Admin handlers registered")
    
    try:
        logger.info("Starting IjaraNazorat Boss bot...")
        await dp.start_polling(admin_bot)
    except Exception as e:
        logger.error(f"Error running admin bot: {e}")
    finally:
        await admin_bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Admin bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
