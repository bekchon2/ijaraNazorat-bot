# IjaraNazorat - Telegram Bot System

A comprehensive dual Telegram bot system for rental property management with tenant tracking, subscription management, and admin oversight capabilities.

## Features

### IjaraNazorat Bot (Main Bot)
- **Multi-language support** (Uzbek/Russian) with flag buttons
- **Phone number authorization** and user profile management
- **Property management** with adding/editing rental properties
- **Tenant management** with passport details and rental dates
- **Subscription system** (monthly: 12,000 som, yearly: 100,000 som)
- **Payment integration** with manual verification process
- **Automated notifications** for rent payments and overdue alerts
- **Comprehensive reporting** system with income analytics

### IjaraNazorat Boss Bot (Admin Bot)
- **Admin authentication** with password protection
- **User management dashboard** showing all bot users
- **Premium request approval** system
- **Statistics dashboard** with user metrics
- **Password change** functionality

## Tech Stack

- **Python 3.10+**
- **aiogram 3.x** (Telegram Bot Framework)
- **SQLAlchemy** (Database ORM)
- **APScheduler** (Task Scheduling)
- **SQLite/PostgreSQL** (Configurable Database)

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ijaranazorat-bot
