from datetime import datetime, timedelta
from typing import Dict, List, Any
from database.database import DatabaseService
from localization.translations import get_text

class ReportService:
    @staticmethod
    async def generate_monthly_report(user_id: int) -> Dict[str, Any]:
        """Generate monthly income report"""
        from database.database import get_session
        from database.models import Tenant, Property
        from sqlalchemy import select, func
        
        async with get_session() as session:
            # Current month start
            now = datetime.now()
            month_start = datetime(now.year, now.month, 1)
            
            # Get user's tenants and their payments
            result = await session.execute(
                select(Tenant, Property)
                .join(Property, Tenant.property_id == Property.id)
                .where(Tenant.landlord_id == user_id)
                .where(Tenant.last_payment_date >= month_start)
            )
            
            tenants_with_properties = result.all()
            
            total_income = 0
            paid_tenants = 0
            properties_count = len(set(tp.property_id for t, p in tenants_with_properties for tp in [t]))
            
            for tenant, property_obj in tenants_with_properties:
                if tenant.payment_status == "paid":
                    total_income += tenant.amount_paid
                    paid_tenants += 1
                elif tenant.payment_status == "partial":
                    total_income += tenant.amount_paid
            
            return {
                "month": now.strftime("%B %Y"),
                "total_income": total_income,
                "paid_tenants": paid_tenants,
                "total_tenants": len(tenants_with_properties),
                "properties_count": properties_count,
                "payment_rate": (paid_tenants / len(tenants_with_properties) * 100) if tenants_with_properties else 0
            }
    
    @staticmethod
    async def generate_yearly_report(user_id: int) -> Dict[str, Any]:
        """Generate yearly income report"""
        from database.database import get_session
        from database.models import Tenant, Property
        from sqlalchemy import select
        
        async with get_session() as session:
            # Current year start
            now = datetime.now()
            year_start = datetime(now.year, 1, 1)
            
            # Get user's tenants and their payments for the year
            result = await session.execute(
                select(Tenant, Property)
                .join(Property, Tenant.property_id == Property.id)
                .where(Tenant.landlord_id == user_id)
                .where(Tenant.last_payment_date >= year_start)
            )
            
            tenants_with_properties = result.all()
            
            monthly_income = {}
            total_income = 0
            
            for tenant, property_obj in tenants_with_properties:
                if tenant.last_payment_date and tenant.payment_status in ["paid", "partial"]:
                    month_key = tenant.last_payment_date.strftime("%Y-%m")
                    if month_key not in monthly_income:
                        monthly_income[month_key] = 0
                    monthly_income[month_key] += tenant.amount_paid
                    total_income += tenant.amount_paid
            
            return {
                "year": now.year,
                "total_income": total_income,
                "monthly_breakdown": monthly_income,
                "average_monthly": total_income / 12 if total_income > 0 else 0,
                "best_month": max(monthly_income.items(), key=lambda x: x[1]) if monthly_income else ("N/A", 0)
            }
    
    @staticmethod
    async def get_overdue_payments(user_id: int) -> List[Dict[str, Any]]:
        """Get overdue payment information"""
        from database.database import get_session
        from database.models import Tenant, Property
        from sqlalchemy import select
        
        async with get_session() as session:
            # Get tenants with overdue payments
            today = datetime.now()
            current_day = today.day
            
            result = await session.execute(
                select(Tenant, Property)
                .join(Property, Tenant.property_id == Property.id)
                .where(Tenant.landlord_id == user_id)
                .where(Tenant.rent_due_date < current_day)
                .where(Tenant.payment_status.in_(["pending", "partial"]))
            )
            
            overdue_list = []
            for tenant, property_obj in result:
                overdue_amount = tenant.amount_due - tenant.amount_paid
                days_overdue = current_day - tenant.rent_due_date
                
                overdue_list.append({
                    "tenant_name": tenant.full_name,
                    "property_address": property_obj.address,
                    "overdue_amount": overdue_amount,
                    "days_overdue": days_overdue,
                    "currency": property_obj.currency,
                    "last_payment": tenant.last_payment_date
                })
            
            return overdue_list
    
    @staticmethod
    def format_monthly_report(report: Dict[str, Any], language: str) -> str:
        """Format monthly report text"""
        month = report["month"]
        income = report["total_income"]
        paid_tenants = report["paid_tenants"]
        total_tenants = report["total_tenants"]
        payment_rate = report["payment_rate"]
        
        if language == "uz":
            text = f"""📊 Oylik hisobot - {month}

💰 Jami daromad: {income:,.0f} so'm
👥 To'lagan ijarachilar: {paid_tenants}/{total_tenants}
📈 To'lov foizi: {payment_rate:.1f}%
🏠 Faol mulklar: {report["properties_count"]} ta"""
        else:  # ru
            text = f"""📊 Месячный отчет - {month}

💰 Общий доход: {income:,.0f} сум
👥 Платящие арендаторы: {paid_tenants}/{total_tenants}
📈 Процент оплат: {payment_rate:.1f}%
🏠 Активная недвижимость: {report["properties_count"]} шт."""
        
        return text
    
    @staticmethod
    def format_yearly_report(report: Dict[str, Any], language: str) -> str:
        """Format yearly report text"""
        year = report["year"]
        income = report["total_income"]
        avg_monthly = report["average_monthly"]
        best_month = report["best_month"]
        
        if language == "uz":
            text = f"""📊 Yillik hisobot - {year}

💰 Jami daromad: {income:,.0f} so'm
📈 O'rtacha oylik: {avg_monthly:.0f} so'm
🏆 Eng yaxshi oy: {best_month[0]} ({best_month[1]:,.0f} so'm)"""
        else:  # ru
            text = f"""📊 Годовой отчет - {year}

💰 Общий доход: {income:,.0f} сум
📈 Средний месячный: {avg_monthly:.0f} сум
🏆 Лучший месяц: {best_month[0]} ({best_month[1]:,.0f} сум)"""
        
        return text
    
    @staticmethod
    def format_overdue_report(overdue_list: List[Dict[str, Any]], language: str) -> str:
        """Format overdue payments report"""
        if not overdue_list:
            if language == "uz":
                return "✅ Kechikkan to'lovlar yo'q!"
            else:
                return "✅ Нет просроченных платежей!"
        
        if language == "uz":
            text = "⚠️ Kechikkan to'lovlar:\n\n"
        else:
            text = "⚠️ Просроченные платежи:\n\n"
        
        for item in overdue_list:
            if language == "uz":
                text += f"👤 {item['tenant_name']}\n"
                text += f"🏠 {item['property_address']}\n"
                text += f"💰 Qarz: {item['overdue_amount']:,.0f} {item['currency']}\n"
                text += f"📅 {item['days_overdue']} kun kechikdi\n\n"
            else:
                text += f"👤 {item['tenant_name']}\n"
                text += f"🏠 {item['property_address']}\n"
                text += f"💰 Долг: {item['overdue_amount']:,.0f} {item['currency']}\n"
                text += f"📅 Просрочено на {item['days_overdue']} дней\n\n"
        
        return text
