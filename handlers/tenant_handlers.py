from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.database import DatabaseService
from keyboards.main_keyboards import tenants_keyboard, tenants_with_actions_keyboard, property_selection_keyboard, cancel_keyboard
from localization.translations import get_text
from utils.helpers import format_tenant_list, format_tenant_list_with_properties, parse_date, is_valid_day
from datetime import datetime

router = Router()

class TenantStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_passport_series = State()
    waiting_for_passport_number = State()
    waiting_for_move_in_date = State()
    waiting_for_property_selection = State()
    waiting_for_due_date = State()
    waiting_for_partial_amount = State()

async def show_tenants(message: Message, user):
    """Show user tenants with property information"""
    tenant_property_pairs = await DatabaseService.get_tenants_with_properties(user.id)
    
    if not tenant_property_pairs:
        text = get_text(user.language, "no_tenants")
        await message.answer(
            text,
            reply_markup=tenants_keyboard(user.language)
        )
    else:
        text = format_tenant_list_with_properties(tenant_property_pairs, user.language)
        await message.answer(
            text,
            reply_markup=tenants_with_actions_keyboard(tenant_property_pairs, user.language)
        )

@router.callback_query(F.data == "add_tenant")
async def add_tenant_handler(callback: CallbackQuery, state: FSMContext):
    """Handle add tenant request"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    # Check if user has properties
    properties = await DatabaseService.get_user_properties(user.id)
    
    if not properties:
        await callback.message.edit_text(get_text(user.language, "no_properties"))
        return
    
    await callback.message.edit_text(get_text(user.language, "enter_tenant_name"))
    await state.set_state(TenantStates.waiting_for_name)
    await state.update_data(language=user.language, user_id=user.id)

@router.message(StateFilter(TenantStates.waiting_for_name))
async def tenant_name_input_handler(message: Message, state: FSMContext):
    """Handle tenant name input"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if message.text == get_text(language, "cancel"):
        await state.clear()
        user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
        await show_tenants(message, user)
        return
    
    await state.update_data(full_name=message.text)
    await message.answer(
        get_text(language, "enter_passport_series"),
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(TenantStates.waiting_for_passport_series)

@router.message(StateFilter(TenantStates.waiting_for_passport_series))
async def passport_series_input_handler(message: Message, state: FSMContext):
    """Handle passport series input"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if message.text == get_text(language, "cancel"):
        await state.clear()
        user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
        await show_tenants(message, user)
        return
    
    await state.update_data(passport_series=message.text)
    await message.answer(
        get_text(language, "enter_passport_number"),
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(TenantStates.waiting_for_passport_number)

@router.message(StateFilter(TenantStates.waiting_for_passport_number))
async def passport_number_input_handler(message: Message, state: FSMContext):
    """Handle passport number input"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if message.text == get_text(language, "cancel"):
        await state.clear()
        user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
        await show_tenants(message, user)
        return
    
    await state.update_data(passport_number=message.text)
    await message.answer(
        get_text(language, "enter_move_in_date"),
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(TenantStates.waiting_for_move_in_date)

@router.message(StateFilter(TenantStates.waiting_for_move_in_date))
async def move_in_date_input_handler(message: Message, state: FSMContext):
    """Handle move-in date input"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if message.text == get_text(language, "cancel"):
        await state.clear()
        user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
        await show_tenants(message, user)
        return
    
    move_in_date = parse_date(message.text)
    if not move_in_date:
        await message.answer(get_text(language, "error"))
        return
    
    await state.update_data(move_in_date=move_in_date)
    
    # Show property selection
    user_id = data.get("user_id")
    properties = await DatabaseService.get_user_properties(user_id)
    
    await message.answer(
        get_text(language, "select_property"),
        reply_markup=property_selection_keyboard(properties, language)
    )
    await state.set_state(TenantStates.waiting_for_property_selection)

@router.callback_query(F.data.startswith("select_property_"), StateFilter(TenantStates.waiting_for_property_selection))
async def property_selection_handler(callback: CallbackQuery, state: FSMContext):
    """Handle property selection"""
    property_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(property_id=property_id)
    await callback.message.edit_text(
        get_text(language, "enter_due_date")
    )
    await state.set_state(TenantStates.waiting_for_due_date)

@router.message(StateFilter(TenantStates.waiting_for_due_date))
async def due_date_input_handler(message: Message, state: FSMContext):
    """Handle rent due date input"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if message.text == get_text(language, "cancel"):
        await state.clear()
        user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
        await show_tenants(message, user)
        return
    
    if not is_valid_day(message.text):
        await message.answer(get_text(language, "error"))
        return
    
    due_date = int(message.text)
    
    # Create tenant
    tenant = await DatabaseService.create_tenant(
        landlord_id=data["user_id"],
        property_id=data["property_id"],
        full_name=data["full_name"],
        passport_series=data["passport_series"],
        passport_number=data["passport_number"],
        move_in_date=data["move_in_date"],
        rent_due_date=due_date
    )
    
    await message.answer(get_text(language, "tenant_added"))
    await state.clear()
    
    # Show updated tenants list
    user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
    await show_tenants(message, user)

@router.callback_query(F.data == "tenants")
async def show_tenants_callback(callback: CallbackQuery):
    """Show tenants via callback"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    await show_tenants(callback.message, user)

# Payment status handlers
@router.callback_query(F.data.startswith("payment_full_"))
async def payment_full_handler(callback: CallbackQuery):
    """Mark payment as fully paid"""
    tenant_id = int(callback.data.split("_")[2])
    
    success = await DatabaseService.update_tenant_payment_status(tenant_id, "paid")
    
    if success:
        await callback.answer("✅ To'lov to'liq to'langan deb belgilandi")
        # Refresh the tenants list
        user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
        await show_tenants(callback.message, user)
    else:
        await callback.answer("❌ Xatolik yuz berdi")

@router.callback_query(F.data.startswith("payment_none_"))
async def payment_none_handler(callback: CallbackQuery):
    """Mark payment as not paid"""
    tenant_id = int(callback.data.split("_")[2])
    
    success = await DatabaseService.update_tenant_payment_status(tenant_id, "overdue")
    
    if success:
        await callback.answer("❌ To'lov to'lanmagan deb belgilandi")
        # Refresh the tenants list
        user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
        await show_tenants(callback.message, user)
    else:
        await callback.answer("❌ Xatolik yuz berdi")

@router.callback_query(F.data.startswith("payment_partial_"))
async def payment_partial_handler(callback: CallbackQuery, state: FSMContext):
    """Handle partial payment"""
    tenant_id = int(callback.data.split("_")[2])
    
    await callback.message.edit_text("💰 Qancha to'langan? (son kiriting):")
    await state.set_state(TenantStates.waiting_for_partial_amount)
    await state.update_data(tenant_id=tenant_id)

@router.message(StateFilter(TenantStates.waiting_for_partial_amount))
async def partial_amount_input_handler(message: Message, state: FSMContext):
    """Handle partial payment amount input"""
    try:
        amount = float(message.text.replace(",", "").replace(" ", ""))
        data = await state.get_data()
        tenant_id = data["tenant_id"]
        
        success = await DatabaseService.update_tenant_payment_status(tenant_id, "partial", amount)
        
        if success:
            await message.answer(f"⚡ Qisman to'lov ({amount:,.0f} so'm) qayd qilindi")
            # Refresh the tenants list
            user = await DatabaseService.get_user_by_telegram_id(message.from_user.id)
            await show_tenants(message, user)
        else:
            await message.answer("❌ Xatolik yuz berdi")
        
        await state.clear()
    except ValueError:
        await message.answer("❌ Noto'g'ri raqam. Qaytadan kiriting:")

@router.callback_query(F.data == "separator")
async def separator_handler(callback: CallbackQuery):
    """Handle separator button (do nothing)"""
    await callback.answer()
