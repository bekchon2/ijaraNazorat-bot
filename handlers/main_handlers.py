from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Contact
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.database import DatabaseService
from keyboards.main_keyboards import (
    language_selection_keyboard, phone_number_keyboard, 
    main_menu_keyboard, profile_keyboard
)
from localization.translations import get_text
from utils.helpers import format_user_info

router = Router()

class MainStates(StatesGroup):
    waiting_for_language = State()
    waiting_for_phone = State()
    waiting_for_name = State()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command"""
    user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        # New user - show language selection
        await message.answer(
            "🌐 Tilni tanlang / Выберите язык:",
            reply_markup=language_selection_keyboard()
        )
        await state.set_state(MainStates.waiting_for_language)
    else:
        # Existing user - show main menu
        await message.answer(
            get_text(user.language, "main_menu"),
            reply_markup=main_menu_keyboard(user.language)
        )

@router.callback_query(F.data.startswith("lang_"))
async def language_selection_handler(callback: CallbackQuery, state: FSMContext):
    """Handle language selection"""
    language = callback.data.split("_")[1]
    
    # Check if user exists
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        # Create new user
        user = await DatabaseService.create_user(callback.from_user.id, language)
        await callback.message.edit_text(get_text(language, "language_selected"))
        
        # Request phone number
        await callback.message.answer(
            get_text(language, "send_phone"),
            reply_markup=phone_number_keyboard(language)
        )
        await state.set_state(MainStates.waiting_for_phone)
    else:
        # Update existing user language
        await DatabaseService.update_user(callback.from_user.id, language=language)
        await callback.message.edit_text(get_text(language, "language_selected"))
        
        # Show main menu
        await callback.message.answer(
            get_text(language, "main_menu"),
            reply_markup=main_menu_keyboard(language)
        )
        await state.clear()

@router.message(F.contact, StateFilter(MainStates.waiting_for_phone))
async def phone_number_handler(message: Message, state: FSMContext):
    """Handle phone number submission"""
    contact: Contact = message.contact
    
    if contact.user_id != message.from_user.id:
        user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
        await message.answer(get_text(user.language, "error"))
        return
    
    # Update user with phone number
    user = await DatabaseService.update_user(
        message.from_user.id, 
        phone_number=contact.phone_number
    )
    
    await message.answer(
        get_text(user.language, "phone_saved"),
        reply_markup=main_menu_keyboard(user.language)
    )
    await state.clear()

@router.message(F.text.in_([
    "🏠 Mulklar", "🏠 Недвижимость",
    "👥 Ijarachilar", "👥 Арендаторы", 
    "📊 Hisobot", "📊 Отчеты",
    "👤 Profil", "👤 Профиль",
    "💎 Obuna", "💎 Подписка"
]))
async def main_menu_handler(message: Message):
    """Handle main menu button presses"""
    user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Please start the bot first with /start")
        return
    
    text = message.text
    
    if text in ["🏠 Mulklar", "🏠 Недвижимость"]:
        from handlers.property_handlers import show_properties
        await show_properties(message, user)
    
    elif text in ["👥 Ijarachilar", "👥 Арендаторы"]:
        from handlers.tenant_handlers import show_tenants
        await show_tenants(message, user)
    
    elif text in ["📊 Hisobot", "📊 Отчеты"]:
        from handlers.report_handlers import show_reports
        await show_reports(message, user)
    
    elif text in ["👤 Profil", "👤 Профиль"]:
        await show_profile(message, user)
    
    elif text in ["💎 Obuna", "💎 Подписка"]:
        from handlers.subscription_handlers import show_subscription
        await show_subscription(message, user)

async def show_profile(message: Message, user):
    """Show user profile"""
    profile_text = format_user_info(user)
    await message.answer(
        profile_text,
        reply_markup=profile_keyboard(user.language)
    )

@router.callback_query(F.data == "edit_profile")
async def edit_profile_handler(callback: CallbackQuery, state: FSMContext):
    """Handle profile editing"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    await callback.message.edit_text(get_text(user.language, "enter_full_name"))
    await state.set_state(MainStates.waiting_for_name)

@router.message(StateFilter(MainStates.waiting_for_name))
async def name_input_handler(message: Message, state: FSMContext):
    """Handle name input"""
    user = await DatabaseService.update_user(
        message.from_user.id,
        full_name=message.text
    )
    
    await message.answer(get_text(user.language, "profile_updated"))
    await show_profile(message, user)
    await state.clear()

@router.callback_query(F.data == "change_language")
async def change_language_handler(callback: CallbackQuery):
    """Handle language change"""
    await callback.message.edit_text(
        "🌐 Tilni tanlang / Выберите язык:",
        reply_markup=language_selection_keyboard()
    )

@router.callback_query(F.data == "back_to_main")
async def back_to_main_handler(callback: CallbackQuery):
    """Handle back to main menu"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    await callback.message.edit_text(
        get_text(user.language, "main_menu"),
        reply_markup=main_menu_keyboard(user.language)
    )
