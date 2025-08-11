from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.database import DatabaseService
from keyboards.main_keyboards import properties_keyboard, currency_keyboard, cancel_keyboard
from localization.translations import get_text
from config import config
from utils.helpers import format_property_list, is_valid_number

router = Router()

class PropertyStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_area = State()
    waiting_for_rooms = State()
    waiting_for_rent = State()
    waiting_for_currency = State()

async def show_properties(message: Message, user):
    """Show user properties"""
    properties = await DatabaseService.get_user_properties(user.id)
    
    if not properties:
        text = get_text(user.language, "no_properties")
    else:
        text = format_property_list(properties, user.language)
    
    await message.answer(
        text,
        reply_markup=properties_keyboard(user.language)
    )

@router.callback_query(F.data == "add_property")
async def add_property_handler(callback: CallbackQuery, state: FSMContext):
    """Handle add property request"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    # Check property limit
    properties = await DatabaseService.get_user_properties(user.id)
    
    if len(properties) >= config.FREE_PROPERTY_LIMIT and not user.is_premium:
        await callback.message.edit_text(
            get_text(user.language, "property_limit_reached")
        )
        return
    
    await callback.message.edit_text(get_text(user.language, "enter_address"))
    await state.set_state(PropertyStates.waiting_for_address)
    await state.update_data(language=user.language)

@router.message(StateFilter(PropertyStates.waiting_for_address))
async def address_input_handler(message: Message, state: FSMContext):
    """Handle address input"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if message.text == get_text(language, "cancel"):
        await state.clear()
        user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
        await show_properties(message, user)
        return
    
    await state.update_data(address=message.text)
    await message.answer(
        get_text(language, "enter_area"),
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(PropertyStates.waiting_for_area)

@router.message(StateFilter(PropertyStates.waiting_for_area))
async def area_input_handler(message: Message, state: FSMContext):
    """Handle area input"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if message.text == get_text(language, "cancel"):
        await state.clear()
        user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
        await show_properties(message, user)
        return
    
    if not is_valid_number(message.text):
        await message.answer(get_text(language, "error"))
        return
    
    area = float(message.text)
    await state.update_data(area_sqm=area)
    await message.answer(
        get_text(language, "enter_rooms"),
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(PropertyStates.waiting_for_rooms)

@router.message(StateFilter(PropertyStates.waiting_for_rooms))
async def rooms_input_handler(message: Message, state: FSMContext):
    """Handle rooms count input"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if message.text == get_text(language, "cancel"):
        await state.clear()
        user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
        await show_properties(message, user)
        return
    
    try:
        rooms = int(message.text)
        if rooms <= 0:
            raise ValueError
    except ValueError:
        await message.answer(get_text(language, "error"))
        return
    
    await state.update_data(rooms_count=rooms)
    await message.answer(
        get_text(language, "enter_rent"),
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(PropertyStates.waiting_for_rent)

@router.message(StateFilter(PropertyStates.waiting_for_rent))
async def rent_input_handler(message: Message, state: FSMContext):
    """Handle rent amount input"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if message.text == get_text(language, "cancel"):
        await state.clear()
        user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
        await show_properties(message, user)
        return
    
    if not is_valid_number(message.text):
        await message.answer(get_text(language, "error"))
        return
    
    rent = float(message.text)
    await state.update_data(monthly_rent=rent)
    await message.answer(
        get_text(language, "select_currency"),
        reply_markup=currency_keyboard(language)
    )
    await state.set_state(PropertyStates.waiting_for_currency)

@router.callback_query(F.data.startswith("currency_"), StateFilter(PropertyStates.waiting_for_currency))
async def currency_selection_handler(callback: CallbackQuery, state: FSMContext):
    """Handle currency selection"""
    currency = callback.data.split("_")[1]
    data = await state.get_data()
    
    # Create property
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    property_obj = await DatabaseService.create_property(
        owner_id=user.id,
        address=data["address"],
        area_sqm=data["area_sqm"],
        rooms_count=data["rooms_count"],
        monthly_rent=data["monthly_rent"],
        currency=currency
    )
    
    language = data.get("language", "uz")
    await callback.message.edit_text(get_text(language, "property_added"))
    await state.clear()
    
    # Show updated properties list
    await show_properties(callback.message, user)

@router.callback_query(F.data == "properties")
async def show_properties_callback(callback: CallbackQuery):
    """Show properties via callback"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    await show_properties(callback.message, user)
