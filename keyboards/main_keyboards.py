from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from localization.translations import get_text, get_language_flag
from typing import List

def language_selection_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data="lang_uz"),
        InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="lang_ru")
    )
    builder.adjust(1)
    return builder.as_markup()

def phone_number_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Phone number request keyboard"""
    text = get_text(language, "phone_button")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def main_menu_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    builder = ReplyKeyboardBuilder()
    
    buttons = [
        get_text(language, "properties"),
        get_text(language, "tenants"),
        get_text(language, "reports"),
        get_text(language, "profile"),
        get_text(language, "subscription")
    ]
    
    for button in buttons:
        builder.add(KeyboardButton(text=button))
    
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

def properties_keyboard(language: str) -> InlineKeyboardMarkup:
    """Properties management keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "add_property"), 
            callback_data="add_property"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "back"), 
            callback_data="back_to_main"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def tenants_keyboard(language: str) -> InlineKeyboardMarkup:
    """Tenants management keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "add_tenant"), 
            callback_data="add_tenant"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "back"), 
            callback_data="back_to_main"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def tenants_with_actions_keyboard(tenant_property_pairs: List, language: str) -> InlineKeyboardMarkup:
    """Tenants list with payment action buttons"""
    builder = InlineKeyboardBuilder()
    
    for tenant, property_obj in tenant_property_pairs:
        # Payment status buttons for each tenant
        builder.add(
            InlineKeyboardButton(
                text="✅ To'liq to'langan", 
                callback_data=f"payment_full_{tenant.id}"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="❌ To'lanmagan", 
                callback_data=f"payment_none_{tenant.id}"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="⚡ Qisman to'langan", 
                callback_data=f"payment_partial_{tenant.id}"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="─────────", 
                callback_data="separator"
            )
        )
    
    # Add tenant and back buttons
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "add_tenant"), 
            callback_data="add_tenant"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "back"), 
            callback_data="back_to_main"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def currency_keyboard(language: str) -> InlineKeyboardMarkup:
    """Currency selection keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text=get_text(language, "uzs"), callback_data="currency_UZS"),
        InlineKeyboardButton(text=get_text(language, "usd"), callback_data="currency_USD")
    )
    builder.adjust(2)
    return builder.as_markup()

def subscription_keyboard(language: str) -> InlineKeyboardMarkup:
    """Subscription keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "monthly_sub"), 
            callback_data="sub_monthly"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "yearly_sub"), 
            callback_data="sub_yearly"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "back"), 
            callback_data="back_to_main"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def payment_confirmation_keyboard(language: str, sub_type: str) -> InlineKeyboardMarkup:
    """Payment confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "payment_made"), 
            callback_data=f"payment_confirm_{sub_type}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "back"), 
            callback_data="subscription"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def profile_keyboard(language: str) -> InlineKeyboardMarkup:
    """Profile management keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "edit_profile"), 
            callback_data="edit_profile"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "change_language"), 
            callback_data="change_language"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "back"), 
            callback_data="back_to_main"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def reports_keyboard(language: str) -> InlineKeyboardMarkup:
    """Reports keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "monthly_report"), 
            callback_data="report_monthly"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "yearly_report"), 
            callback_data="report_yearly"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "overdue_payments"), 
            callback_data="report_overdue"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "back"), 
            callback_data="back_to_main"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def property_selection_keyboard(properties: List, language: str) -> InlineKeyboardMarkup:
    """Property selection keyboard for tenant assignment"""
    builder = InlineKeyboardBuilder()
    
    for prop in properties:
        builder.add(
            InlineKeyboardButton(
                text=f"🏠 {prop.address[:30]}...", 
                callback_data=f"select_property_{prop.id}"
            )
        )
    
    builder.add(
        InlineKeyboardButton(
            text=get_text(language, "back"), 
            callback_data="tenants"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def cancel_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Cancel operation keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=get_text(language, "cancel")))
    return builder.as_markup(resize_keyboard=True)
