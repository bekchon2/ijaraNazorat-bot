from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.database import DatabaseService
from keyboards.admin_keyboards import (
    admin_main_keyboard, users_list_keyboard, user_detail_keyboard,
    premium_requests_keyboard, premium_request_detail_keyboard
)
from config import config
from utils.helpers import format_admin_user_info, format_premium_request_info

router = Router()

class AdminStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_new_password = State()

@router.message(CommandStart())
async def admin_start_handler(message: Message, state: FSMContext):
    """Handle admin /start command"""
    if message.from_user.id != config.ADMIN_TELEGRAM_ID:
        await message.answer("🚫 Sizga ruxsat berilmagan")
        return
    
    # Check if already authenticated
    is_authenticated = await DatabaseService.authenticate_admin(message.from_user.id)
    
    if is_authenticated:
        await message.answer(
            "👋 Admin panel",
            reply_markup=admin_main_keyboard()
        )
    else:
        await message.answer("🔐 Parolni kiriting:")
        await state.set_state(AdminStates.waiting_for_password)

@router.message(StateFilter(AdminStates.waiting_for_password))
async def admin_password_handler(message: Message, state: FSMContext):
    """Handle admin password input"""
    if message.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    # Check database password first, then fallback to config
    saved_password = await DatabaseService.get_admin_config("admin_password", config.ADMIN_PASSWORD)
    
    if message.text == saved_password:
        # Create admin session
        await DatabaseService.create_admin_session(message.from_user.id)
        
        await message.answer(
            "✅ Parol to'g'ri! Admin panelga xush kelibsiz.",
            reply_markup=admin_main_keyboard()
        )
        await state.clear()
    else:
        await message.answer("❌ Noto'g'ri parol. Qaytadan kiriting:")

@router.callback_query(F.data == "admin_main")
async def admin_main_handler(callback: CallbackQuery):
    """Show admin main menu"""
    if callback.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    await callback.message.edit_text(
        "👋 Admin panel",
        reply_markup=admin_main_keyboard()
    )

@router.callback_query(F.data.startswith("admin_users"))
async def admin_users_handler(callback: CallbackQuery):
    """Handle users list request"""
    if callback.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    if callback.data == "admin_users":
        page = 0
    else:
        # admin_users_page_X
        page = int(callback.data.split("_")[-1])
    
    users = await DatabaseService.get_all_users()
    
    text = f"👥 Foydalanuvchilar ro'yxati ({len(users)} ta):"
    
    await callback.message.edit_text(
        text,
        reply_markup=users_list_keyboard(users, page)
    )

@router.callback_query(F.data.startswith("admin_user_"))
async def admin_user_detail_handler(callback: CallbackQuery):
    """Handle individual user details"""
    if callback.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    user_id = int(callback.data.split("_")[2])
    
    # Get user info
    users = await DatabaseService.get_all_users()
    user = next((u for u in users if u.id == user_id), None)
    
    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi")
        return
    
    user_info = format_admin_user_info(user)
    
    await callback.message.edit_text(
        user_info,
        reply_markup=user_detail_keyboard(user.id, user.is_premium)
    )

@router.callback_query(F.data.startswith("admin_activate_premium_"))
async def admin_activate_premium_handler(callback: CallbackQuery):
    """Handle premium activation"""
    if callback.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    user_id = int(callback.data.split("_")[3])
    
    # Activate premium (1 year)
    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(days=365)
    
    await DatabaseService.update_user(
        telegram_id=None,  # We don't have telegram_id here, need to modify function
        user_id=user_id,
        is_premium=True,
        premium_expires_at=expires_at
    )
    
    await callback.answer("✅ Premium faollashtirildi!")
    
    # Refresh user detail
    users = await DatabaseService.get_all_users()
    user = next((u for u in users if u.id == user_id), None)
    user_info = format_admin_user_info(user)
    
    await callback.message.edit_text(
        user_info,
        reply_markup=user_detail_keyboard(user.id, user.is_premium)
    )

@router.callback_query(F.data == "admin_premium_requests")
async def admin_premium_requests_handler(callback: CallbackQuery):
    """Handle premium requests list"""
    if callback.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    requests = await DatabaseService.get_pending_premium_requests()
    
    text = f"💎 Premium so'rovlar ({len(requests)} ta):"
    
    await callback.message.edit_text(
        text,
        reply_markup=premium_requests_keyboard(requests)
    )

@router.callback_query(F.data.startswith("admin_premium_req_"))
async def admin_premium_request_detail_handler(callback: CallbackQuery):
    """Handle premium request details"""
    if callback.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    request_id = int(callback.data.split("_")[3])
    
    # Get request info
    requests = await DatabaseService.get_pending_premium_requests()
    request = next((r for r in requests if r.id == request_id), None)
    
    if not request:
        await callback.answer("❌ So'rov topilmadi")
        return
    
    request_info = format_premium_request_info(request)
    
    await callback.message.edit_text(
        request_info,
        reply_markup=premium_request_detail_keyboard(request.id)
    )

@router.callback_query(F.data.startswith("admin_approve_premium_"))
async def admin_approve_premium_handler(callback: CallbackQuery):
    """Handle premium request approval"""
    if callback.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    request_id = int(callback.data.split("_")[3])
    
    success = await DatabaseService.approve_premium_request(request_id)
    
    if success:
        # Get request to send notification to user
        requests = await DatabaseService.get_pending_premium_requests()
        request = next((r for r in requests if r.id == request_id), None)
        
        if request:
            try:
                from services.notification_service import NotificationService
                await NotificationService.notify_user_premium_activated(request.user)
            except Exception as e:
                print(f"Failed to send user notification: {e}")
        
        await callback.message.edit_text("✅ Premium so'rov tasdiqlandi!")
    else:
        await callback.answer("❌ Xatolik yuz berdi")

@router.callback_query(F.data == "admin_stats")
async def admin_stats_handler(callback: CallbackQuery):
    """Handle statistics request"""
    if callback.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    stats = await DatabaseService.get_user_stats()
    
    stats_text = f"""📊 Statistika:

👥 Jami foydalanuvchilar: {stats['total_users']}
💎 Premium foydalanuvchilar: {stats['premium_users']}
📅 Oxirgi 7 kunda qo'shilganlar: {stats['recent_users']}
💰 Premium foizi: {(stats['premium_users']/stats['total_users']*100):.1f}%"""
    
    await callback.message.edit_text(stats_text)

@router.callback_query(F.data == "admin_change_password")
async def admin_change_password_handler(callback: CallbackQuery, state: FSMContext):
    """Handle password change request"""
    if callback.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    await callback.message.edit_text("🔐 Yangi parolni kiriting:")
    await state.set_state(AdminStates.waiting_for_new_password)

@router.message(StateFilter(AdminStates.waiting_for_new_password))
async def admin_new_password_handler(message: Message, state: FSMContext):
    """Handle new password input"""
    if message.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    # Save new password to database
    new_password = message.text.strip()
    await DatabaseService.set_admin_config("admin_password", new_password)
    
    await message.answer(
        "✅ Parol o'zgartirildi va saqlandi!",
        reply_markup=admin_main_keyboard()
    )
    await state.clear()

@router.callback_query(F.data == "admin_logout")
async def admin_logout_handler(callback: CallbackQuery):
    """Handle admin logout"""
    if callback.from_user.id != config.ADMIN_TELEGRAM_ID:
        return
    
    # Remove admin session
    from database.database import get_session
    from database.models import AdminSession
    from sqlalchemy import delete
    
    async with get_session() as session:
        await session.execute(
            delete(AdminSession).where(AdminSession.telegram_id == callback.from_user.id)
        )
        await session.commit()
    
    await callback.message.edit_text("👋 Admin paneldan chiqildi.")
