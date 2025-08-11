from typing import Dict, Any

# Translation dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "uz": {
        # Language selection
        "select_language": "🌐 Tilni tanlang:",
        "language_selected": "✅ Til tanlandi: O'zbek tili",
        
        # Phone number
        "send_phone": "📱 Telefon raqamingizni yuboring:",
        "phone_button": "📞 Telefon raqamini yuborish",
        "phone_saved": "✅ Telefon raqam saqlandi!",
        
        # Main menu
        "main_menu": "🏠 Asosiy menyu:",
        "properties": "🏠 Mulklar",
        "tenants": "👥 Ijarachilar", 
        "reports": "📊 Hisobot",
        "profile": "👤 Profil",
        "subscription": "💎 Obuna",
        
        # Properties
        "my_properties": "🏠 Mening mulklarim:",
        "add_property": "➕ Mulk qo'shish",
        "no_properties": "❌ Sizda hali mulk yo'q",
        "property_limit_reached": "⚠️ Bepul limit tugadi! Premium obuna sotib oling.",
        "enter_address": "🏠 Manzilni kiriting:",
        "enter_area": "📐 Maydonni kiriting (m²):",
        "enter_rooms": "🏠 Xonalar sonini kiriting:",
        "enter_rent": "💰 Oylik ijara summasini kiriting:",
        "select_currency": "💱 Valyutani tanlang:",
        "property_added": "✅ Mulk muvaffaqiyatli qo'shildi!",
        
        # Tenants
        "my_tenants": "👥 Mening ijarachilarim:",
        "add_tenant": "➕ Ijarachi qo'shish",
        "no_tenants": "❌ Sizda hali ijarachi yo'q",
        "enter_tenant_name": "👤 Ijarachi F.I.Sh ni kiriting:",
        "enter_passport_series": "📋 Passport seriyasini kiriting:",
        "enter_passport_number": "📋 Passport raqamini kiriting:",
        "enter_move_in_date": "📅 Kirish sanasini kiriting (DD.MM.YYYY):",
        "select_property": "🏠 Mulkni tanlang:",
        "enter_due_date": "📅 To'lov kunini kiriting (1-31):",
        "tenant_added": "✅ Ijarachi muvaffaqiyatli qo'shildi!",
        
        # Subscription
        "subscription_info": "💎 Obuna ma'lumotlari:",
        "monthly_sub": "📅 Oylik obuna (12,000 so'm)",
        "yearly_sub": "📅 Yillik obuna (100,000 so'm)",
        "payment_info": "💳 To'lov ma'lumotlari:\nKarta: 9860350140898858\nEgasi: BEKCHANOV B.",
        "payment_made": "✅ To'lov qildim",
        "premium_request_sent": "✅ So'rovingiz yuborildi! Admin tekshiradi.",
        
        # Profile
        "profile_info": "👤 Profil ma'lumotlari:",
        "edit_profile": "✏️ Profilni tahrirlash",
        "change_language": "🌐 Tilni o'zgartirish",
        "enter_full_name": "👤 F.I.Sh ni kiriting:",
        "profile_updated": "✅ Profil yangilandi!",
        
        # Reports
        "reports_menu": "📊 Hisobot menyusi:",
        "income_report": "💰 Daromad hisoboti",
        "monthly_report": "📅 Oylik hisobot",
        "yearly_report": "📅 Yillik hisobot",
        "overdue_payments": "⚠️ Kechikkan to'lovlar",
        
        # Payment statuses
        "payment_paid": "✅ To'liq to'langan",
        "payment_pending": "⏳ To'lanmagan",
        "payment_partial": "⚠️ Qisman to'langan",
        "payment_overdue": "❌ Muddati o'tgan",
        
        # Notifications
        "rent_reminder": "🔔 To'lov eslatmasi:\n{tenant_name} - {property_address}\nTo'lov muddati: {days} kun qoldi",
        "rent_overdue": "⚠️ To'lov muddati o'tdi:\n{tenant_name} - {property_address}\nQarzlik: {amount} {currency}",
        
        # Common
        "back": "⬅️ Orqaga",
        "cancel": "❌ Bekor qilish",
        "confirm": "✅ Tasdiqlash",
        "error": "❌ Xatolik yuz berdi",
        "success": "✅ Muvaffaqiyatli",
        "uzs": "🇺🇿 So'm",
        "usd": "💵 Dollar",
    },
    
    "ru": {
        # Language selection
        "select_language": "🌐 Выберите язык:",
        "language_selected": "✅ Язык выбран: Русский",
        
        # Phone number
        "send_phone": "📱 Отправьте свой номер телефона:",
        "phone_button": "📞 Отправить номер телефона",
        "phone_saved": "✅ Номер телефона сохранен!",
        
        # Main menu
        "main_menu": "🏠 Главное меню:",
        "properties": "🏠 Недвижимость",
        "tenants": "👥 Арендаторы",
        "reports": "📊 Отчеты",
        "profile": "👤 Профиль",
        "subscription": "💎 Подписка",
        
        # Properties
        "my_properties": "🏠 Моя недвижимость:",
        "add_property": "➕ Добавить недвижимость",
        "no_properties": "❌ У вас пока нет недвижимости",
        "property_limit_reached": "⚠️ Бесплатный лимит исчерпан! Купите премиум подписку.",
        "enter_address": "🏠 Введите адрес:",
        "enter_area": "📐 Введите площадь (м²):",
        "enter_rooms": "🏠 Введите количество комнат:",
        "enter_rent": "💰 Введите месячную арендную плату:",
        "select_currency": "💱 Выберите валюту:",
        "property_added": "✅ Недвижимость успешно добавлена!",
        
        # Tenants
        "my_tenants": "👥 Мои арендаторы:",
        "add_tenant": "➕ Добавить арендатора",
        "no_tenants": "❌ У вас пока нет арендаторов",
        "enter_tenant_name": "👤 Введите Ф.И.О арендатора:",
        "enter_passport_series": "📋 Введите серию паспорта:",
        "enter_passport_number": "📋 Введите номер паспорта:",
        "enter_move_in_date": "📅 Введите дату заселения (ДД.ММ.ГГГГ):",
        "select_property": "🏠 Выберите недвижимость:",
        "enter_due_date": "📅 Введите день оплаты (1-31):",
        "tenant_added": "✅ Арендатор успешно добавлен!",
        
        # Subscription
        "subscription_info": "💎 Информация о подписке:",
        "monthly_sub": "📅 Месячная подписка (12,000 сум)",
        "yearly_sub": "📅 Годовая подписка (100,000 сум)",
        "payment_info": "💳 Информация для оплаты:\nКарта: 9860350140898858\nВладелец: BEKCHANOV B.",
        "payment_made": "✅ Я оплатил",
        "premium_request_sent": "✅ Ваш запрос отправлен! Админ проверит.",
        
        # Profile
        "profile_info": "👤 Информация профиля:",
        "edit_profile": "✏️ Редактировать профиль",
        "change_language": "🌐 Изменить язык",
        "enter_full_name": "👤 Введите Ф.И.О:",
        "profile_updated": "✅ Профиль обновлен!",
        
        # Reports
        "reports_menu": "📊 Меню отчетов:",
        "income_report": "💰 Отчет о доходах",
        "monthly_report": "📅 Месячный отчет",
        "yearly_report": "📅 Годовой отчет",
        "overdue_payments": "⚠️ Просроченные платежи",
        
        # Payment statuses
        "payment_paid": "✅ Полностью оплачено",
        "payment_pending": "⏳ Не оплачено",
        "payment_partial": "⚠️ Частично оплачено",
        "payment_overdue": "❌ Просрочено",
        
        # Notifications
        "rent_reminder": "🔔 Напоминание об оплате:\n{tenant_name} - {property_address}\nДо оплаты осталось: {days} дней",
        "rent_overdue": "⚠️ Срок оплаты прошел:\n{tenant_name} - {property_address}\nЗадолженность: {amount} {currency}",
        
        # Common
        "back": "⬅️ Назад",
        "cancel": "❌ Отмена",
        "confirm": "✅ Подтвердить",
        "error": "❌ Произошла ошибка",
        "success": "✅ Успешно",
        "uzs": "🇺🇿 Сум",
        "usd": "💵 Доллар",
    }
}

def get_text(language: str, key: str, **kwargs) -> str:
    """Get localized text"""
    text = TRANSLATIONS.get(language, TRANSLATIONS["uz"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

def get_language_flag(language: str) -> str:
    """Get language flag emoji"""
    flags = {
        "uz": "🇺🇿",
        "ru": "🇷🇺"
    }
    return flags.get(language, "🌐")
