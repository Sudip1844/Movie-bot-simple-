#!/usr/bin/env python3
"""
Telegram Movie Bot - A role-based movie distribution bot using Supabase storage
"""

import os
import uuid
import logging
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Telegram Bot imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes, ConversationHandler, JobQueue
)

# Supabase imports
from supabase import create_client, Client

# Other imports
from dotenv import load_dotenv
from fuzzywuzzy import fuzz

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OWNER_USER_ID = int(os.getenv("OWNER_USER_ID", "0"))

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Conversation states
(ADDING_MOVIE_TITLE, SELECTING_UPLOAD_TYPE, SELECTING_QUALITY, 
 UPLOADING_FILE, UPLOADING_EPISODE, ADMIN_USER_ID, REMOVE_ADMIN_USER_ID,
 SEARCH_MOVIE, REMOVE_MOVIE_SEARCH, REMOVE_MOVIE_CONFIRM) = range(10)

# Role constants
ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"
ROLE_USER = "user"

# --- Helper Functions for Auto-Deleting Messages ---

async def delete_message_job(context: ContextTypes.DEFAULT_TYPE):
    """Job to delete a message."""
    job_context = context.job.data
    chat_id = job_context["chat_id"]
    message_id = job_context["message_id"]
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Deleted message {message_id} from chat {chat_id}")
    except Exception as e:
        logger.warning(f"Could not delete message {message_id} from chat {chat_id}: {e}")

async def reply_with_autodelete(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, **kwargs):
    """Reply to a message and schedule its deletion after 48 hours for admins/owner."""
    user_id = update.effective_user.id
    role = await DatabaseManager.get_user_role(user_id)
    
    message = await update.message.reply_text(text, **kwargs)

    if role in [ROLE_OWNER, ROLE_ADMIN]:
        # Schedule deletion after 48 hours (172800 seconds)
        context.job_queue.run_once(
            delete_message_job,
            172800,
            data={"chat_id": message.chat_id, "message_id": message.message_id},
            name=f"delete_{message.chat_id}_{message.message_id}"
        )

async def edit_with_autodelete(query, context: ContextTypes.DEFAULT_TYPE, text: str, **kwargs):
    """Edit a message and schedule its deletion after 48 hours for admins/owner."""
    user_id = query.from_user.id
    role = await DatabaseManager.get_user_role(user_id)

    message = await query.edit_message_text(text, **kwargs)

    if role in [ROLE_OWNER, ROLE_ADMIN]:
        context.job_queue.run_once(
            delete_message_job,
            172800,
            data={"chat_id": message.chat_id, "message_id": message.message_id},
            name=f"delete_{message.chat_id}_{message.message_id}"
        )


class DatabaseManager:
    """Handles all database operations with Supabase"""

    @staticmethod
    async def get_user_role(user_id: int) -> str:
        """Get user role from database"""
        if user_id == OWNER_USER_ID:
            return ROLE_OWNER
        try:
            result = supabase.table("users").select("role").eq("telegram_id", user_id).single().execute()
            if result.data:
                return result.data["role"]
            return ROLE_USER
        except Exception:
            return ROLE_USER

    @staticmethod
    async def set_user_role(user_id: int, role: str) -> bool:
        """Set user role in database"""
        try:
            # Upsert user role
            supabase.table("users").upsert({
                "telegram_id": user_id,
                "role": role,
                "created_at": datetime.utcnow().isoformat()
            }, on_conflict="telegram_id").execute()
            return True
        except Exception as e:
            logger.error(f"Error setting user role: {e}")
            return False

    # ... (rest of DatabaseManager methods remain the same as your original file) ...
    @staticmethod
    async def remove_user_role(user_id: int) -> bool:
        """Remove user admin role (set to user)"""
        try:
            supabase.table("users").update({"role": ROLE_USER}).eq("telegram_id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error removing user role: {e}")
            return False

    @staticmethod
    async def create_movie(title: str, movie_type: str, created_by: int) -> Optional[int]:
        """Create a new movie entry"""
        try:
            result = supabase.table("movies").insert({
                "title": title,
                "type": movie_type,
                "created_by": created_by,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            if result.data:
                return result.data[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error creating movie: {e}")
            return None

    @staticmethod
    async def add_movie_file(movie_id: int, quality: str, file_id: str, episode_number: Optional[int] = None) -> bool:
        """Add a movie file to database"""
        try:
            supabase.table("movie_files").insert({
                "movie_id": movie_id,
                "quality": quality,
                "file_id": file_id,
                "episode_number": episode_number,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding movie file: {e}")
            return False

    @staticmethod
    async def create_download_token(movie_id: int, quality: Optional[str] = None, episode_number: Optional[int] = None) -> str:
        """Create a download token for sharing"""
        try:
            token = str(uuid.uuid4())

            supabase.table("download_tokens").insert({
                "token": token,
                "movie_id": movie_id,
                "quality": quality,
                "episode_number": episode_number,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            return token
        except Exception as e:
            logger.error(f"Error creating download token: {e}")
            return ""

    @staticmethod
    async def get_token_info(token: str) -> Optional[Dict]:
        """Get token information for download"""
        try:
            result = supabase.table("download_tokens").select("*").eq("token", token).single().execute()
            if result.data:
                return result.data
            return None
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return None

    @staticmethod
    async def search_movies(query: str) -> List[Dict]:
        """Search movies with fuzzy matching"""
        try:
            result = supabase.table("movies").select("*").execute()
            movies = result.data or []
            matches = [
                movie for movie in movies
                if fuzz.partial_ratio(query.lower(), movie["title"].lower()) >= 50
            ]
            matches.sort(key=lambda x: fuzz.partial_ratio(query.lower(), x["title"].lower()), reverse=True)
            return matches
        except Exception as e:
            logger.error(f"Error searching movies: {e}")
            return []

    @staticmethod
    async def get_movie_files(movie_id: int) -> List[Dict]:
        """Get all files for a movie"""
        try:
            result = supabase.table("movie_files").select("*").eq("movie_id", movie_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting movie files: {e}")
            return []

    @staticmethod
    async def delete_movie(movie_id: int) -> bool:
        """Delete movie and all associated data"""
        try:
            supabase.table("movie_files").delete().eq("movie_id", movie_id).execute()
            supabase.table("download_tokens").delete().eq("movie_id", movie_id).execute()
            supabase.table("movies").delete().eq("id", movie_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting movie: {e}")
            return False


class BotHandlers:
    """Contains all bot command and callback handlers"""

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id

        if context.args:
            token = context.args[0]
            await BotHandlers.handle_token_download(update, context, token)
            return

        role = await DatabaseManager.get_user_role(user_id)
        welcome_message = "🎬 Welcome to Movie Distribution Bot!\n\n"
        if role == ROLE_OWNER:
            welcome_message += (
                "👑 Owner Commands:\n"
                "/add_admin - Add an admin\n"
                "/remove_admin - Remove an admin\n"
                "/add_movie - Add a new movie\n"
                "/remove_movie - Remove a movie\n"
                "/search - Search for movies\n"
            )
            await reply_with_autodelete(update, context, welcome_message)
        elif role == ROLE_ADMIN:
            welcome_message += (
                "👨‍💼 Admin Commands:\n"
                "/add_movie - Add a new movie\n"
                "/search - Search for movies\n"
            )
            await reply_with_autodelete(update, context, welcome_message)
        else:
            welcome_message += (
                "👤 User Access:\n"
                "You can access movies through shared links only.\n\n"
                "❓ How to Use MovieZone Bot\n\n"
                "🎭 Request - Request new movies to admin: @Xmafia007\n\n"
                "Download Process:\n"
                "1. 🔍 Search or browse for a movie in our channel @moviezone969\n"
                "2. 📱 Select quality (480p/720p/1080p)links or\n"
                "Series download link\n"
                "3. 👀 Watch ads\n"
                "4. 📥 Get your movie!\n\n"
                "Tips:\n"
                "• Use specific movie names for better search results in channel\n"
                "• Check our channel for latest uploads\n"
                "• Report any issues to admins\n\n"
                "Support: @Xmafia007\n"
                "Join: @moviezone969\n\n"
                "🎬 Happy watching!"
            )
            await update.message.reply_text(welcome_message)
            
    # ... (handle_token_download and admin management handlers are mostly the same, but use autodelete helpers) ...
    # Here's an example of changing one admin function. Apply this to others.
    
    @staticmethod
    async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        role = await DatabaseManager.get_user_role(user_id)
        if role != ROLE_OWNER:
            await reply_with_autodelete(update, context, "❌ This command is only available to the owner.")
            return ConversationHandler.END
        await reply_with_autodelete(update, context, "👨‍💼 Please send the Telegram User ID of the user you want to make admin:")
        return ADMIN_USER_ID

    @staticmethod
    async def receive_admin_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            admin_user_id = int(update.message.text.strip())
            success = await DatabaseManager.set_user_role(admin_user_id, ROLE_ADMIN)
            if success:
                await reply_with_autodelete(update, context, f"✅ User {admin_user_id} has been granted admin privileges.")
            else:
                await reply_with_autodelete(update, context, "❌ Failed to grant admin privileges.")
        except ValueError:
            await reply_with_autodelete(update, context, "❌ Invalid User ID. Please send a valid number.")
            return ADMIN_USER_ID
        return ConversationHandler.END

    # --- MOVIE UPLOAD FLOW (FIXED) ---
    
    @staticmethod
    async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        role = await DatabaseManager.get_user_role(user_id)
        if role not in [ROLE_OWNER, ROLE_ADMIN]:
            await reply_with_autodelete(update, context, "❌ You don't have permission to add movies.")
            return ConversationHandler.END
        await reply_with_autodelete(update, context, "🎬 Please enter the movie title:")
        return ADDING_MOVIE_TITLE

    @staticmethod
    async def receive_movie_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        title = update.message.text.strip()
        context.user_data["movie_title"] = title
        keyboard = [
            [InlineKeyboardButton("🎬 Upload Single Movie File", callback_data="upload_single")],
            [InlineKeyboardButton("📺 Upload Multiple Series (Episodes)", callback_data="upload_series")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"📽️ Movie: {title}\n\nPlease select upload type:",
            reply_markup=reply_markup
        )
        return SELECTING_UPLOAD_TYPE

    @staticmethod
    async def handle_upload_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        upload_type = query.data
        context.user_data["upload_type"] = upload_type
        if upload_type == "upload_single":
            context.user_data["movie_type"] = "single"
            context.user_data["uploaded_qualities"] = []
            keyboard = [
                [InlineKeyboardButton("480p", callback_data="quality_480p")],
                [InlineKeyboardButton("720p", callback_data="quality_720p")],
                [InlineKeyboardButton("1080p", callback_data="quality_1080p")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("📱 Select quality for the movie file:", reply_markup=reply_markup)
            return SELECTING_QUALITY
        else:
            context.user_data["movie_type"] = "series"
            context.user_data["episode_count"] = 0
            await query.edit_message_text("📺 Please upload Episode 1:")
            return UPLOADING_EPISODE

    @staticmethod
    async def handle_quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        quality = query.data.replace("quality_", "")
        context.user_data["selected_quality"] = quality
        await query.edit_message_text(f"📤 Please upload the movie file for {quality} quality:")
        return UPLOADING_FILE

    @staticmethod
    async def receive_movie_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message.document:
            await reply_with_autodelete(update, context, "❌ Please upload a file.")
            return UPLOADING_FILE
        try:
            if "movie_id" not in context.user_data:
                movie_id = await DatabaseManager.create_movie(
                    context.user_data["movie_title"], "single", update.effective_user.id)
                if not movie_id:
                    await reply_with_autodelete(update, context, "❌ Failed to create movie entry.")
                    return ConversationHandler.END
                context.user_data["movie_id"] = movie_id
            
            file_id = update.message.document.file_id
            quality = context.user_data["selected_quality"]
            await DatabaseManager.add_movie_file(context.user_data["movie_id"], quality, file_id)
            context.user_data.setdefault("uploaded_qualities", []).append(quality)
            
            all_qualities = ["480p", "720p", "1080p"]
            remaining_qualities = [q for q in all_qualities if q not in context.user_data["uploaded_qualities"]]
            
            if remaining_qualities:
                keyboard = [[InlineKeyboardButton(q, callback_data=f"quality_{q}")] for q in remaining_qualities]
                keyboard.append([InlineKeyboardButton("✅ Finish Upload", callback_data="no_more_qualities")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"✅ {quality} file uploaded!\nSelect another quality or finish:",
                    reply_markup=reply_markup
                )
                return SELECTING_QUALITY # Return to quality selection state
            else:
                await BotHandlers.generate_single_movie_links(update, context)
                return ConversationHandler.END
        except Exception as e:
            logger.error(f"Error in receive_movie_file: {e}")
            await reply_with_autodelete(update, context, "❌ Error processing file upload.")
            return ConversationHandler.END

    @staticmethod
    async def handle_no_more_qualities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        await BotHandlers.generate_single_movie_links(query, context) # Pass query instead of update
        return ConversationHandler.END

    @staticmethod
    async def generate_single_movie_links(update_or_query, context) -> None:
        try:
            movie_id = context.user_data["movie_id"]
            movie_title = context.user_data["movie_title"]
            uploaded_qualities = context.user_data["uploaded_qualities"]
            message = f"🎬 **{movie_title}**\n\n📥 Download Links:\n"
            bot_username = context.bot.username
            for quality in sorted(uploaded_qualities):
                token = await DatabaseManager.create_download_token(movie_id, quality)
                if token:
                    download_link = f"https://t.me/{bot_username}?start={token}"
                    message += f"🔗 {quality}: {download_link}\n"
            
            if isinstance(update_or_query, Update):
                await reply_with_autodelete(update_or_query, context, message, parse_mode="Markdown")
            else: # It's a CallbackQuery
                await edit_with_autodelete(update_or_query, context, message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error generating single movie links: {e}")
            # Handle error display
    
    @staticmethod
    async def receive_episode_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message.document:
            await reply_with_autodelete(update, context, "❌ Please upload a file.")
            return UPLOADING_EPISODE
        try:
            if "movie_id" not in context.user_data:
                movie_id = await DatabaseManager.create_movie(
                    context.user_data["movie_title"], "series", update.effective_user.id)
                if not movie_id:
                    await reply_with_autodelete(update, context, "❌ Failed to create movie entry.")
                    return ConversationHandler.END
                context.user_data["movie_id"] = movie_id
            
            file_id = update.message.document.file_id
            episode_number = context.user_data.get("episode_count", 0) + 1
            await DatabaseManager.add_movie_file(
                context.us
