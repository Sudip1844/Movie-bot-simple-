# Telegram Movie Bot

## Overview

This is a Python-based Telegram bot designed for movie distribution with role-based access control. The bot uses Supabase as its backend database, allowing users to upload, search, and download movies with different permission levels (owner, admin, user).

### New Features
- **Auto Chat Cleanup**: For Owners and Admins, bot messages are automatically deleted after 48 hours to keep the chat interface clean.
- **Data Expiration**: All movie data (including files and download tokens) is automatically deleted from the database after 4 years (48 months) using a Supabase Cron Job.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a single-file monolithic architecture with the following key design decisions:

### Backend Architecture
- **Framework**: Python with `python-telegram-bot` library.
- **Database**: Supabase (PostgreSQL-based) for data persistence.
- **Authentication**: Role-based system (Owner, Admin, User).
- **File Handling**: Direct Telegram file API usage.
- **Scheduled Tasks**: Utilizes `python-telegram-bot`'s `JobQueue` for chat cleanup and Supabase Cron Jobs for database maintenance.

### Communication Pattern
- **Bot Interface**: Telegram Bot API.
- **Conversation Flow**: `ConversationHandler` pattern for multi-step interactions.
- **Callback System**: Inline keyboards for interactive menus.

## Key Components

### 1. User Management System
- **Owner**: Full administrative privileges.
- **Admin**: Movie management capabilities.
- **User**: Search and download permissions.

### 2. Movie Management
- **Upload System**: Multi-quality (480p, 720p, 1080p) and TV series (episodes) support.
- **Search Functionality**: Fuzzy search with `fuzzywuzzy`.
- **Metadata Storage**: Titles, file IDs, quality, and creation timestamps.
- **Data Lifecycle**: Movie data automatically expires and is deleted after 48 months.

### 3. Conversation & Chat Management
- **State Machine**: `ConversationHandler` for various operations.
- **Context Preservation**: User session management during multi-step operations.
- **Admin Chat Cleanup**: Bot-sent messages to admins/owner are auto-deleted after 48 hours to prevent clutter.

## Data Flow

### Movie Upload Flow (Fixed)
1. Admin/Owner starts the upload command.
2. Bot asks for the title, then type (movie/series).
3. **Movie**: User selects a quality, uploads the file. The bot then offers remaining quality options or a "Finish" button.
4. **Series**: User uploads Episode 1. The bot then asks for the next episode or a "Finish" button.
5. Bot stores metadata in Supabase.
6. Confirmation with download links is sent and scheduled for deletion after 48 hours.

## Deployment Strategy

### Database Requirements
- Supabase account and project.
- Tables for `users`, `movies`, `movie_files`, `download_tokens`.
- **(New)** A Supabase Cron Job must be configured to run daily to enforce the 4-year data expiration policy.

---
