# Overview

IjaraNazorat is a comprehensive dual Telegram bot system designed for rental property management. The system consists of two interconnected bots: the main IjaraNazorat Bot for property owners and tenants, and the IjaraNazorat Boss Bot for administrative oversight. The platform enables property owners to manage multiple rental properties, track tenants, handle subscription payments, and receive automated notifications for rent collection, while administrators can oversee user activities and approve premium requests.

## Current Status (August 9, 2025)
✅ **System fully operational** - Both bots running successfully  
✅ **Main Bot (@ijaraNazoratbot)** - Property management interface active  
✅ **Admin Bot (@ijaraNazorat_boss_bot)** - Administrative dashboard running  
✅ **PostgreSQL Database** - Connected and initialized with all tables  
✅ **Automated Notifications** - Rent reminders and overdue alerts scheduled  
✅ **Payment Processing** - Manual verification system with admin approval workflow

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Architecture
The system implements a dual-bot architecture using aiogram 3.x framework:
- **Main Bot (main_bot.py)**: Handles property owner interactions, tenant management, subscription processing, and automated notifications
- **Admin Bot (admin_bot.py)**: Provides administrative controls for user management, premium request approvals, and system statistics

Both bots share a common database and configuration system, enabling seamless data synchronization between user-facing and administrative functions.

## State Management
Uses aiogram's FSM (Finite State Machine) for complex user interactions:
- Multi-step property registration flows
- Tenant onboarding processes with passport validation
- Subscription payment workflows
- Administrative authentication sequences

## Database Design
Built with SQLAlchemy ORM using async patterns for optimal performance:
- **Users**: Core user profiles with telegram_id, language preferences, premium status
- **Properties**: Property details including address, area, room count, rental amounts
- **Tenants**: Tenant information with passport details, move-in dates, payment tracking
- **Subscriptions**: Payment records and premium membership tracking
- **PremiumRequests**: Pending premium upgrade requests for admin approval
- **AdminSessions**: Administrative authentication and session management

The database supports both SQLite (development) and PostgreSQL (production) through configurable connection strings.

## Internationalization
Implements a comprehensive translation system supporting Uzbek and Russian languages:
- Flag-based language selection interface
- Dynamic text rendering based on user language preferences
- Localized keyboards and message formatting
- Cultural adaptations for date formats and currency displays

## Payment Processing
Manual payment verification system with structured workflow:
- Subscription tiers (monthly: 12,000 som, yearly: 100,000 som)
- Premium request generation and admin approval process
- Payment confirmation through administrative bot
- Automated premium status activation and expiration tracking

## Notification System
APScheduler-based automated notification service:
- Daily rent payment reminders (configurable days in advance)
- Overdue payment notifications
- Cron-based scheduling for consistent delivery timing
- Multi-language notification templates

## Report Generation
Comprehensive analytics and reporting capabilities:
- Monthly income reports with payment rate analysis
- Yearly financial summaries
- Overdue payment tracking and tenant management
- Property utilization and tenant occupancy statistics

# External Dependencies

## Core Framework Dependencies
- **aiogram 3.x**: Modern async Telegram Bot API framework for Python
- **SQLAlchemy**: Database ORM with async support for database operations
- **APScheduler**: Advanced Python Scheduler for automated notification delivery

## Database Systems
- **SQLite**: Default development database with aiosqlite async adapter
- **PostgreSQL**: Production database option with asyncpg driver support

## Telegram Bot API
- **Telegram Bot API**: Official Telegram messaging platform integration
- **Webhook/Polling**: Configurable message delivery mechanisms

## Python Runtime
- **Python 3.10+**: Required for modern async/await syntax and type hinting support
- **asyncio**: Built-in async runtime for concurrent operation handling

## Development Tools
- **Environment Variables**: Configuration management through system environment
- **Logging**: Built-in Python logging for debugging and monitoring
- **Type Hints**: Full typing support for better code maintenance and IDE integration