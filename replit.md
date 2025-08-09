# MovieZone Telegram Bot

## Overview
MovieZone is a Telegram bot designed for movie discovery, sharing, and request management. It allows users to search for movies, browse by categories, request new content, and access direct movie downloads. The bot features a robust role-based access control system for owners, administrators, and regular users, aiming to provide a user-friendly experience for movie enthusiasts.

## User Preferences
Preferred communication style: Simple, everyday language.
All bot commands are available only through reply keyboard buttons.
The hamburger menu is completely removed; during conversations, it is empty.
The "❌ Cancel" button appears in the reply keyboard alongside other commands during conversations.
The `/cancel` command is available via command box input.
The bot should not make changes to the `BOT_TOKEN` in `config.py`.
Updated category system with specific emoji icons and two special categories:
- "All 🌐" for alphabet-based movie filtering (user types letter, bot shows movies starting with that letter)
- "Hentai 💦" available only in admin movie addition interface, not in user browsing

## System Architecture
The application adopts a modular architecture, promoting separation of concerns and maintainability.

### UI/UX Decisions
- **Interaction Model**: Exclusively uses reply keyboard buttons for all user interactions, eliminating the hamburger menu.
- **Cancel Mechanism**: A "❌ Cancel" button is integrated into reply keyboards during conversations, with `/cancel` command also supported via text input.
- **Dynamic Command Menu**: The command menu dynamically hides during ongoing conversations and restores upon completion.
- **Category Browsing**: Movies within categories are displayed in a 3x10 grid format with pagination and navigation.
- **Message Formatting**: Professional, structured layouts with emojis and clear information hierarchy are used, with all bold formatting removed.
- **Channel Message Filtering**: The bot only responds to search queries in private chats, ignoring channel posts unless specifically made through the bot's movie addition workflow.
- **Admin/Channel Management**: Features are integrated into existing commands and accessed via dedicated buttons (e.g., "Manage Admins" includes "Add New Admin", "Remove an Admin") using short names for identification.

### Technical Implementations
- **Core Framework**: Built on the `python-telegram-bot` library.
- **Configuration**: Centralized in `config.py` for environment variables, constants, and message templates.
- **Data Storage**: Uses a JSON-based file system (`database.py`) for all data (users, admins, movies, channels, requests, tokens), ensuring easy backup and migration.
- **Handler Modules**: Organized handlers for specific functionalities (Start, Movie Search, Conversation, Callback, Owner actions) ensure modularity.
- **Utility Functions**: `utils.py` provides common functionalities like role-based access control (`@restricted` decorator), keyboard generation, movie post formatting, and direct download link generation.
- **Role-Based Access Control**: Strict permissions (Owner, Admin, User) are enforced via decorators and dynamic keyboard generation.
- **Command Management**: Per-chat command scope management controls command visibility dynamically.
- **Conversation Handling**: Multi-step conversations are managed with robust cancellation logic and simplified to reduce API calls by avoiding complex message editing.
- **Ad/Download Integration**: Supports direct movie downloads.
- **User Registration**: Automatic registration on `/start` command with role-appropriate welcome messages shown only for new users.
- **Movie Search & Browse**: Users can search by query or browse categories with detailed movie information and direct download options.
- **Movie Request System**: Users can submit movie requests, which admins can manage. Users are notified upon fulfillment, and requests are paginated for efficient management.
- **Admin & Owner Features**: Comprehensive management of users, movies, channels, and requests.
- **Movie Management**: Owner role includes full movie lifecycle management with "➕ Add Movie", "🗑️ Remove Movie", and "📊 Show Stats" functionality, including uploader information and download counts.
- **Skip Functionality**: Added skip buttons to movie addition process for metadata (release year, runtime, IMDb rating), categories, and languages, using sensible defaults and hiding skipped fields from posts. Movie addition now uses direct download link inputs instead of file uploads.
- **Automated Posting**: After preview, movies can be posted to multiple selected channels with validation checks.
- **Message Cleanup**: A two-tier automatic chat cleanup system with step-by-step conversation cleanup during workflows and a 24-hour scheduled deletion for user/admin/owner messages. Movie posts are preserved for regular users.
- **UI/UX Improvements**: Enhanced skip button behavior for category selection (similar to language selection), consolidated step messages to reduce duplication, improved navigation control for request pagination (hides buttons when 5 or fewer requests), and dynamic cancel button behavior for channel selection.
- **Command Box Stability**: Fixed conversation handler command box disable issues by adding per_message=True to all ConversationHandlers and implementing proper keyboard restoration after movie addition completion. Enhanced restore_main_keyboard function to handle callback queries properly.
- **Direct Download Links**: Replaced bot URL redirects with actual file URLs in download links while keeping external link confirmation popup. Updated movie browsing/search to use post format instead of quality buttons for consistent user experience with direct links that show confirmation before opening.

## External Dependencies
- `python-telegram-bot`: Primary library for Telegram Bot API interaction.
- `json`: Used for file-based data persistence.
- `os`: For environment variable access and file system operations.
- `logging`: For application logging and debugging.
- `hashlib`: Used for token generation and security features.
- `datetime`: For time-based operations and scheduling.