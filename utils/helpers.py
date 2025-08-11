from datetime import datetime
from typing import List, Optional, Any
from database.models import User, Property, Tenant, PremiumRequest
from localization.translations import get_text

def format_user_info(user: User) -> str:
    """Format user profile information"""
    language = user.language
    
    name = user.full_name or "Noma'lum" if language == "uz" else user.full_name or "Неизвестно"
    phone = user.phone_number or "Noma'lum" if language == "uz" else user.phone_number or "Неизвестно"
    premium_status = "✅ Faol" if user.is_premium else "❌ Faol emas"
    
    if language == "ru":
        premium_status = "✅ Активен" if user.is_premium else "❌ Неактивен"
    
    if language == "uz":
        text = f"""👤 Profil ma'lumotlari:

📝 F.I.Sh: {name}
📞 Telefon: {phone}
🌐 Til: O'zbek
💎 Premium: {premium_status}"""
    else:
        text = f"""👤 Информация профиля:

📝 Ф.И.О: {name}
📞 Телефон: {phone}
🌐 Язык: Русский
💎 Премиум: {premium_status}"""
    
    if user.is_premium and user.premium_expires_at:
        expires = user.premium_expires_at.strftime("%d.%m.%Y")
        if language == "uz":
            text += f"\n⏰ Amal qilish muddati: {expires}"
        else:
            text += f"\n⏰ Действует до: {expires}"
    
    return text

def format_property_list(properties: List[Property], language: str) -> str:
    """Format properties list"""
    if language == "uz":
        text = f"🏠 Mening mulklarim ({len(properties)} ta):\n\n"
    else:
        text = f"🏠 Моя недвижимость ({len(properties)} шт.):\n\n"
    
    for i, prop in enumerate(properties, 1):
        currency_symbol = "💵" if prop.currency == "USD" else "🇺🇿"
        
        if language == "uz":
            text += f"{i}. 📍 {prop.address}\n"
            text += f"   📐 {prop.area_sqm} m² | 🏠 {prop.rooms_count} xona\n"
            text += f"   💰 {prop.monthly_rent:,.0f} {prop.currency} {currency_symbol}\n\n"
        else:
            text += f"{i}. 📍 {prop.address}\n"
            text += f"   📐 {prop.area_sqm} м² | 🏠 {prop.rooms_count} комн.\n"
            text += f"   💰 {prop.monthly_rent:,.0f} {prop.currency} {currency_symbol}\n\n"
    
    return text

def format_tenant_list_with_properties(tenant_property_pairs: List, language: str) -> str:
    """Format tenants list with property information"""
    if language == "uz":
        text = f"👥 Mening ijarachilarim ({len(tenant_property_pairs)} ta):\n\n"
    else:
        text = f"👥 Мои арендаторы ({len(tenant_property_pairs)} шт.):\n\n"
    
    for i, (tenant, property_obj) in enumerate(tenant_property_pairs, 1):
        # Format payment status
        status_icons = {
            "paid": "✅",
            "pending": "⏳",
            "partial": "⚠️",
            "overdue": "❌"
        }
        
        status_icon = status_icons.get(tenant.payment_status, "⏳")
        
        # Calculate days until/past due date
        current_date = datetime.now()
        current_day = current_date.day
        due_date = tenant.rent_due_date
        
        if current_day <= due_date:
            days_left = due_date - current_day
            if language == "uz":
                due_text = f"📅 {days_left} kun qoldi"
            else:
                due_text = f"📅 {days_left} дней осталось"
        else:
            days_overdue = current_day - due_date
            if language == "uz":
                due_text = f"⚠️ {days_overdue} kun kechikdi"
            else:
                due_text = f"⚠️ {days_overdue} дней просрочено"
        
        # Property address (short form)
        property_name = property_obj.address[:30] + "..." if len(property_obj.address) > 30 else property_obj.address
        
        if language == "uz":
            text += f"{i}. 👤 {tenant.full_name}\n"
            text += f"   📋 {tenant.passport_series}{tenant.passport_number}\n"
            text += f"   🏠 {property_name}\n"
            text += f"   📅 Kirgan: {tenant.move_in_date.strftime('%d.%m.%Y')}\n"
            text += f"   💰 Holat: {status_icon}\n"
            text += f"   {due_text}\n\n"
        else:
            text += f"{i}. 👤 {tenant.full_name}\n"
            text += f"   📋 {tenant.passport_series}{tenant.passport_number}\n"
            text += f"   🏠 {property_name}\n"
            text += f"   📅 Заселился: {tenant.move_in_date.strftime('%d.%m.%Y')}\n"
            text += f"   💰 Статус: {status_icon}\n"
            text += f"   {due_text}\n\n"
    
    return text

def format_tenant_list(tenants: List[Tenant], language: str) -> str:
    """Format tenants list (legacy)"""
    if language == "uz":
        text = f"👥 Mening ijarachilarim ({len(tenants)} ta):\n\n"
    else:
        text = f"👥 Мои арендаторы ({len(tenants)} шт.):\n\n"
    
    for i, tenant in enumerate(tenants, 1):
        # Format payment status
        status_icons = {
            "paid": "✅",
            "pending": "⏳",
            "partial": "⚠️",
            "overdue": "❌"
        }
        
        status_texts = {
            "uz": {
                "paid": "To'langan",
                "pending": "Kutilmoqda",
                "partial": "Qisman",
                "overdue": "Kechikkan"
            },
            "ru": {
                "paid": "Оплачено",
                "pending": "Ожидается",
                "partial": "Частично",
                "overdue": "Просрочено"
            }
        }
        
        status_icon = status_icons.get(tenant.payment_status, "❓")
        status_text = status_texts[language].get(tenant.payment_status, tenant.payment_status)
        
        move_in = tenant.move_in_date.strftime("%d.%m.%Y")
        
        if language == "uz":
            text += f"{i}. 👤 {tenant.full_name}\n"
            text += f"   📋 {tenant.passport_series} {tenant.passport_number}\n"
            text += f"   📅 Kirgan: {move_in}\n"
            text += f"   💰 Holat: {status_icon} {status_text}\n\n"
        else:
            text += f"{i}. 👤 {tenant.full_name}\n"
            text += f"   📋 {tenant.passport_series} {tenant.passport_number}\n"
            text += f"   📅 Заселен: {move_in}\n"
            text += f"   💰 Статус: {status_icon} {status_text}\n\n"
    
    return text

def format_subscription_info(user: User, language: str) -> str:
    """Format subscription information"""
    from config import config
    
    if language == "uz":
        text = "💎 Obuna ma'lumotlari:\n\n"
        
        if user.is_premium:
            expires = user.premium_expires_at.strftime("%d.%m.%Y") if user.premium_expires_at else "Noma'lum"
            text += f"✅ Premium faol\n"
            text += f"⏰ Amal qilish muddati: {expires}\n\n"
        else:
            text += "❌ Premium faol emas\n\n"
        
        text += f"💰 Narxlar:\n"
        text += f"📅 Oylik: {config.MONTHLY_SUBSCRIPTION_PRICE:,} so'm\n"
        text += f"📅 Yillik: {config.YEARLY_SUBSCRIPTION_PRICE:,} so'm\n\n"
        text += f"✨ Premium imkoniyatlari:\n"
        text += f"• Cheksiz mulk qo'shish\n"
        text += f"• Kengaytirilgan hisobotlar\n"
        text += f"• Avtomatik eslatmalar\n"
    else:
        text = "💎 Информация о подписке:\n\n"
        
        if user.is_premium:
            expires = user.premium_expires_at.strftime("%d.%m.%Y") if user.premium_expires_at else "Неизвестно"
            text += f"✅ Премиум активен\n"
            text += f"⏰ Действует до: {expires}\n\n"
        else:
            text += "❌ Премиум неактивен\n\n"
        
        text += f"💰 Цены:\n"
        text += f"📅 Месячная: {config.MONTHLY_SUBSCRIPTION_PRICE:,} сум\n"
        text += f"📅 Годовая: {config.YEARLY_SUBSCRIPTION_PRICE:,} сум\n\n"
        text += f"✨ Возможности премиум:\n"
        text += f"• Неограниченное добавление недвижимости\n"
        text += f"• Расширенные отчеты\n"
        text += f"• Автоматические напоминания\n"
    
    return text

def format_admin_user_info(user: User) -> str:
    """Format user info for admin panel"""
    name = user.full_name or f"User_{user.telegram_id}"
    phone = user.phone_number or "Noma'lum"
    language = "O'zbek" if user.language == "uz" else "Русский"
    premium_status = "✅ Faol" if user.is_premium else "❌ Faol emas"
    
    text = f"""👤 Foydalanuvchi: {name}

🆔 ID: {user.id}
📱 Telegram ID: {user.telegram_id}
📞 Telefon: {phone}
🌐 Til: {language}
💎 Premium: {premium_status}
📅 Ro'yxatdan o'tgan: {user.created_at.strftime('%d.%m.%Y %H:%M')}"""
    
    if user.is_premium and user.premium_expires_at:
        text += f"\n⏰ Premium tugaydi: {user.premium_expires_at.strftime('%d.%m.%Y')}"
    
    return text

def format_premium_request_info(request: PremiumRequest) -> str:
    """Format premium request info for admin"""
    user = request.user
    user_name = user.full_name or f"User_{user.telegram_id}"
    phone = user.phone_number or "Noma'lum"
    sub_type = "Oylik" if request.subscription_type == "monthly" else "Yillik"
    
    text = f"""💎 Premium so'rov

👤 Foydalanuvchi: {user_name}
📞 Telefon: {phone}
💰 Summa: {request.amount:,} so'm
📅 Obuna turi: {sub_type}
🕐 So'rov vaqti: {request.requested_at.strftime('%d.%m.%Y %H:%M')}

Tasdiqlaysizmi?"""
    
    return text

def is_valid_number(text: str) -> bool:
    """Check if text is a valid number"""
    try:
        float(text)
        return True
    except ValueError:
        return False

def is_valid_day(text: str) -> bool:
    """Check if text is a valid day of month (1-31)"""
    try:
        day = int(text)
        return 1 <= day <= 31
    except ValueError:
        return False

def parse_date(date_string: str) -> Optional[datetime]:
    """Parse date string in DD.MM.YYYY format"""
    try:
        return datetime.strptime(date_string, "%d.%m.%Y")
    except ValueError:
        try:
            return datetime.strptime(date_string, "%d/%m/%Y")
        except ValueError:
            return None
