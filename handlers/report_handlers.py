from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.database import DatabaseService
from keyboards.main_keyboards import reports_keyboard
from localization.translations import get_text
from services.report_service import ReportService

router = Router()

async def show_reports(message: Message, user):
    """Show reports menu"""
    await message.answer(
        get_text(user.language, "reports_menu"),
        reply_markup=reports_keyboard(user.language)
    )

@router.callback_query(F.data == "report_monthly")
async def monthly_report_handler(callback: CallbackQuery):
    """Handle monthly report request"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    report = await ReportService.generate_monthly_report(user.id)
    report_text = ReportService.format_monthly_report(report, user.language)
    
    await callback.message.edit_text(report_text)

@router.callback_query(F.data == "report_yearly")
async def yearly_report_handler(callback: CallbackQuery):
    """Handle yearly report request"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    report = await ReportService.generate_yearly_report(user.id)
    report_text = ReportService.format_yearly_report(report, user.language)
    
    await callback.message.edit_text(report_text)

@router.callback_query(F.data == "report_overdue")
async def overdue_report_handler(callback: CallbackQuery):
    """Handle overdue payments report"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    
    overdue_tenants = await ReportService.get_overdue_payments(user.id)
    report_text = ReportService.format_overdue_report(overdue_tenants, user.language)
    
    await callback.message.edit_text(report_text)

@router.callback_query(F.data == "reports")
async def show_reports_callback(callback: CallbackQuery):
    """Show reports via callback"""
    user = await DatabaseService.get_user_by_telegram_id(callback.from_user.id)
    await show_reports(callback.message, user)
