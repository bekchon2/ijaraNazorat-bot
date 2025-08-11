from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

def admin_main_keyboard() -> InlineKeyboardMarkup:
    """Admin main menu keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="👥 Foydalanuvchilar ro'yxati", callback_data="admin_users"),
        InlineKeyboardButton(text="💎 Premium so'rovlar", callback_data="admin_premium_requests")
    )
    builder.add(
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
        InlineKeyboardButton(text="🔐 Parolni o'zgartirish", callback_data="admin_change_password")
    )
    builder.add(
        InlineKeyboardButton(text="🚪 Chiqish", callback_data="admin_logout")
    )
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def users_list_keyboard(users: List, page: int = 0, per_page: int = 10) -> InlineKeyboardMarkup:
    """Users list with pagination"""
    builder = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_users = users[start_idx:end_idx]
    
    for user in page_users:
        premium_status = "💎" if user.is_premium else "👤"
        user_name = user.full_name or f"User_{user.telegram_id}"
        
        builder.add(
            InlineKeyboardButton(
                text=f"{premium_status} {user_name}", 
                callback_data=f"admin_user_{user.id}"
            )
        )
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"admin_users_page_{page-1}")
        )
    
    if end_idx < len(users):
        nav_buttons.append(
            InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"admin_users_page_{page+1}")
        )
    
    if nav_buttons:
        for btn in nav_buttons:
            builder.add(btn)
    
    builder.add(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_main")
    )
    
    builder.adjust(1)
    return builder.as_markup()

def user_detail_keyboard(user_id: int, is_premium: bool) -> InlineKeyboardMarkup:
    """Individual user management keyboard"""
    builder = InlineKeyboardBuilder()
    
    if not is_premium:
        builder.add(
            InlineKeyboardButton(
                text="💎 Premium ochish", 
                callback_data=f"admin_activate_premium_{user_id}"
            )
        )
    else:
        builder.add(
            InlineKeyboardButton(
                text="❌ Premium yopish", 
                callback_data=f"admin_deactivate_premium_{user_id}"
            )
        )
    
    builder.add(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_users")
    )
    builder.adjust(1)
    return builder.as_markup()

def premium_requests_keyboard(requests: List) -> InlineKeyboardMarkup:
    """Premium requests management keyboard"""
    builder = InlineKeyboardBuilder()
    
    for request in requests:
        user_name = request.user.full_name or f"User_{request.user.telegram_id}"
        sub_type = "Oylik" if request.subscription_type == "monthly" else "Yillik"
        
        builder.add(
            InlineKeyboardButton(
                text=f"💰 {user_name} - {sub_type}", 
                callback_data=f"admin_premium_req_{request.id}"
            )
        )
    
    builder.add(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_main")
    )
    builder.adjust(1)
    return builder.as_markup()

def premium_request_detail_keyboard(request_id: int) -> InlineKeyboardMarkup:
    """Premium request detail management"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="✅ Premium tasdiqlash", 
            callback_data=f"admin_approve_premium_{request_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="❌ Rad etish", 
            callback_data=f"admin_reject_premium_{request_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_premium_requests")
    )
    builder.adjust(1)
    return builder.as_markup()
