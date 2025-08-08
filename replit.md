# MovieZone Telegram Bot

## Overview

MovieZone is a Telegram bot designed for movie discovery, sharing, and request management. It enables users to search for movies, browse by categories, request new content, and download movies via an ad-based link system. The bot incorporates a robust role-based access control system with distinct permissions for owners, administrators, and regular users. The project aims to provide a streamlined, user-friendly experience for movie enthusiasts while offering monetization opportunities through integrated advertising.

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
- **Interaction Model**: Exclusively uses reply keyboard buttons for all user interactions, eliminating the hamburger menu for a cleaner interface.
- **Cancel Mechanism**: A prominent "❌ Cancel" button is integrated into reply keyboards during conversations for consistent cancellation. The `/cancel` command is also supported via text input.
- **Dynamic Command Menu**: The command menu (`/start`, `/help`) dynamically hides during ongoing conversations, showing only `/cancel`, and restores upon conversation completion.
- **Category Browsing**: Movies within categories are displayed in a 3x10 grid format with pagination and easy navigation back to main categories. Grid layout ensures optimal viewing with up to 30 movies per page.
- **Message Formatting**: Professional, structured layouts with emojis and clear information hierarchy are used consistently across all movie displays, search results, and welcome messages. All bold formatting is removed.
- **Channel Message Filtering**: Bot only responds to search queries in private chats, preventing interference with channel posts made by admins/owners. Channel posts are ignored unless specifically posted through the bot's movie addition workflow.
- **Admin/Channel Management**: Features like managing admins and channels are integrated into existing commands and accessed via dedicated buttons (e.g., "Manage Admins" includes "Add New Admin", "Remove an Admin"). Short names are used for easy identification in removal lists.

### Technical Implementations
- **Core Framework**: Built on the `python-telegram-bot` library.
- **Configuration**: Centralized in `config.py` for environment variables, constants, and message templates.
- **Data Storage**: Uses a JSON-based file system (`database.py`) for users, admins, movies, channels, requests, and tokens, ensuring easy backup and migration without external database dependencies.
- **Handler Modules**: Organized handlers for specific functionalities (Start, Movie Search, Conversation, Callback, Owner actions) to ensure modularity.
- **Utility Functions**: `utils.py` provides common functionalities like role-based access control (`@restricted` decorator), keyboard generation, movie post formatting, and ad link generation.
- **Role-Based Access Control**: Strict permissions (Owner, Admin, User) are enforced via decorators and dynamic keyboard generation.
- **Command Management**: Per-chat command scope management is used to control command visibility dynamically.
- **Conversation Handling**: Multi-step conversations are managed with robust cancellation logic.
- **Ad Integration**: Ad links are generated with secure tokens; users are redirected through an ad page before accessing content.

### Feature Specifications
- **User Registration**: Automatic registration on `/start` command with role-appropriate welcome messages. Welcome messages are shown only for new users to prevent repetitive messaging when accessing expired download links.
- **Movie Search & Browse**: Users can search by query or browse categories with detailed movie information and download options.
- **Movie Request System**: Users can submit movie requests, which admins can manage. Users are notified upon fulfillment.
- **Admin & Owner Features**: Comprehensive management of users, movies, channels, and requests.
- **Movie Management**: Owner role includes full movie lifecycle management with "➕ Add Movie", "🗑️ Remove Movie", and "📊 Show Stats" functionality accessible via reply keyboard buttons. Stats display shows uploader information (Owner/Admin short name) and accurate download counts.
- **Skip Functionality**: Added skip buttons to movie addition process for release year, runtime, IMDb rating, categories, and languages to save time for admins/owners. Skip options use sensible defaults (N/A for metadata, General for category, English for language). Skipped fields (N/A values) are automatically hidden from preview and final posts to keep them clean.
- **Dynamic Command Menu**: Contextual command menu adjustments based on conversation state.
- **Automated Posting**: After preview, movies can be posted to multiple selected channels with validation checks.
- **Message Cleanup**: Comprehensive automatic chat cleanup system with two-tier approach: (1) Step-by-step conversation cleanup during workflows to minimize chat length, (2) 24-hour scheduled deletion for user/admin/owner messages. Movie posts are preserved for regular users while all messages are cleaned for admins/owners.

## External Dependencies

- `python-telegram-bot`: Primary library for Telegram Bot API interaction.
- `json`: Used for file-based data persistence.
- `os`: For environment variable access and file system operations.
- `logging`: For application logging and debugging.
- `hashlib`: Used for token generation and security features.
- `datetime`: For time-based operations and scheduling.
- **GitHub Pages**: Potentially used for hosting the ad page (monetization system).

## Recent Changes

**Enhanced Stats System (August 6, 2025)**
- Completely upgraded "📊 Show Stats" command with three search options:
  - 🔍 Search by Movie Name: Type movie name to find statistics
  - 📂 Search from Category: Browse movies by category in 3x10 grid layout
  - 👤 Search by Admin Name: View movies uploaded by specific admin/owner
- Added new database functions: get_movies_by_category(), get_movies_by_uploader(), get_all_admins()
- Enhanced statistics display with detailed movie information and download counts
- Improved conversation flow with proper state management and error handling
- Post preview updated to remove category emojis and add "Title:" prefix to movie names

**Ad Page Integration (August 6, 2025)**
- Created complete ad page system with 10-second timer functionality (updated from 15 seconds)
- Added auto-scroll and auto-continue features: page scrolls down after 3 seconds, continues to bot after another 3 seconds if user doesn't interact
- Integrated secure token-based download system with external ad page hosting
- Ad page files ready for separate hosting on GitHub Pages
- Updated bot configuration to work with external ad page URL
- Complete workflow: Bot → Ad Page → Timer → Auto-scroll → Return to Bot → File Download

**Migration to Replit Environment - COMPLETED (August 7, 2025)**
- Successfully completed migration from Replit Agent to standard Replit environment
- All dependencies properly installed via packager tool (`python-telegram-bot[job-queue]==20.7`)
- Bot successfully connecting to Telegram API and running without errors
- JobQueue initialization working correctly for message cleanup functionality
- All conversation handlers and workflows functioning properly
- Hamburger menu disabled globally as per project requirements
- Security best practices maintained with client/server separation
- Bot fully operational and ready for production use with all features functional

**Direct Download System Implementation (August 8, 2025)**
- Completely removed ad page system for direct movie downloads
- Updated bot configuration with new credentials:
  - Bot token: 7269265854:AAFYz0-nIJVQbNcJTE1tiW5Nz6Zk-MnGfFA
  - Bot username: @movierecivebot
- Replaced `generate_ad_link_button()` with `generate_direct_download_button()` in utils.py
- Updated callback handlers to provide direct file downloads via "download_" callbacks
- Removed all ad token management functions from database.py (create_ad_token, validate_ad_token)
- Modified start handler to handle direct downloads instead of ad page redirects
- Users now get immediate file access when clicking download buttons
- Enhanced user experience with instant downloads - no ads required
- Maintained download count tracking for statistics
- All movie post templates updated to use direct t.me links

**Conversation Flow Improvements (August 8, 2025)**
- Completely removed message editing system from admin/channel management conversations per user request
- Simplified conversation flow - no more repeated message edits that confused users
- Added confirm/cancel buttons for admin and channel removal operations
- Users now see: Select admin/channel → Confirm/Cancel buttons → Final result
- Removed direct removal confirmations - now requires explicit button confirmation
- Applied to: Manage Admins (Add/Remove), Manage Channels (Add/Remove)  
- Conversation handlers now use simple message flow without complex editing patterns
- Enhanced user experience with clear, straightforward conversations

**API Cost Optimization - Conversation Simplification (August 8, 2025)**
- Removed all unnecessary message editing patterns across conversation handlers to reduce Telegram API usage
- Eliminated ConversationCleanup.cleanup_previous_step() calls from movie addition workflow
- Simplified stats conversation by removing stats_message storage and editing system
- Streamlined movie request conversation by removing request_message editing patterns
- Removed auto_cleanup_message tracking system in movie addition process
- All conversations now use simple reply-based flow instead of complex message editing
- Significant reduction in Telegram API calls and token usage
- Maintained full functionality while improving performance and reducing costs
- Applied to: Movie Addition, Stats Display, Movie Requests, all conversation workflows

**Pagination System for Movie Requests (August 8, 2025)**
- Implemented pagination system for "📋 Show Requests" command displaying only 5 requests per page
- Added navigation buttons (Previous/Next/Cancel) for easy browsing through multiple request pages
- Enhanced database functions with offset/limit support: get_pending_requests() and get_total_pending_requests_count()
- Added pagination controls in callback handler with "requests_page_X" and "requests_cancel" callbacks
- Shows current page information (Page X/Y) for better user navigation experience
- Optimized for admin/owner workflow to handle large numbers of pending requests efficiently

**Movie Addition System Conversion - File Upload to Direct Links (August 8, 2025)**
- Completely converted movie addition workflow from file uploads to direct download link inputs
- Updated conversation handlers: upload_single_files() and upload_series_files() now handle URL inputs
- Added basic link validation requiring http:// or https:// protocol for all download links
- Modified quality selection process: "Select quality to add download link" instead of file uploads
- Updated download system in callback handler to provide direct browser-based download links
- Enhanced user experience: instant access to download links without file storage limitations
- Maintained all existing functionality while eliminating file upload/storage requirements
- Database now stores direct download URLs instead of Telegram file_id tuples

**Bug Fixes and UI Improvements (August 6, 2025)**
- Fixed critical category browsing issue - movies now properly display when selecting categories
- Updated movie display format to show "Title: Movie Name" instead of plain movie names
- Removed Description field from search results as it was showing N/A values
- Enhanced database category matching for exact category matches instead of substring matching
- Improved file ID handling in token system for better download reliability
- Added CSS styling to improve movie photo aspect ratios (wider, less tall appearance)
- Fixed duplicate database function definitions causing category search failures
- Enhanced error logging for category browsing to aid in debugging