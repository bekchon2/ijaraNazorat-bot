from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.database import DatabaseService
from keyboards.main_keyboards import subscription_keyboard, payment_confirmation_keyboard
from localization.translations import get_text
from config import config
from utils.helpers import format_subscription_info

router = Router()

async def show_subscription(message: Message, user):
    """Show subscription information"""
    text = format_subscription_info(user, user.language)
    await message.answer(
        text,
        reply_markup=subscription_keyboard(user.language)
    )

@router.callback_query(F.data.startswith("sub_"))
async def subscription_type_handler(callback: CallbackQuery):
    """Handle subscription type selection"""
    sub_type = callback.data.split("_")[1]  # monthly or yearly
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    if sub_type == "monthly":
        amount = config.MONTHLY_SUBSCRIPTION_PRICE
    else:  # yearly
        amount = config.YEARLY_SUBSCRIPTION_PRICE
    
    payment_info = get_text(user.language, "payment_info")
    price_text = f"💰 {amount:,} so'm"
    
    # Updated payment instruction with card details
    card_info = f"""💳 To'lov ma'lumotlari:
📱 Karta raqami: {config.PAYMENT_CARD_NUMBER}
👤 Egasi: {config.PAYMENT_RECIPIENT}

To'lab bo'lgandan keyin pastdagi "To'lov qildim" tugmasini bosing."""
    
    text = f"{payment_info}\n\n{price_text}\n\n{card_info}"
    
    await callback.message.edit_text(
        text,
        reply_markup=payment_confirmation_keyboard(user.language, sub_type)
    )

@router.callback_query(F.data.startswith("payment_confirm_"))
async def payment_confirmation_handler(callback: CallbackQuery):
    """Handle payment confirmation"""
    sub_type = callback.data.split("_")[2]  # monthly or yearly
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    if sub_type == "monthly":
        amount = config.MONTHLY_SUBSCRIPTION_PRICE
    else:  # yearly
        amount = config.YEARLY_SUBSCRIPTION_PRICE
    
    # Create premium request
    await DatabaseService.create_premium_request(
        user_id=user.id,
        subscription_type=sub_type,
        amount=amount
    )
    
    # Send notification to admin
    try:
        from services.notification_service import NotificationService
        await NotificationService.notify_admin_payment_request(user, sub_type, amount)
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
    
    await callback.message.edit_text(
        get_text(user.language, "premium_request_sent")
    )

@router.callback_query(F.data == "subscription")
async def show_subscription_callback(callback: CallbackQuery):
    """Show subscription via callback"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    await show_subscription(callback.message, user)
