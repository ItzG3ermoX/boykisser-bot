import discord
import random
import re
import json
import os
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
from groq import Groq

# --- ENV LOAD ---
load_dotenv(dotenv_path=".env.kiss")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- LOAD PRESETS ---
with open("slang_presets.json", "r", encoding="utf-8") as f:
    presets = json.load(f)

# --- LOAD USER MEMORY ---
MEMORY_FILE = "user_memory.json"
if os.path.isfile(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        user_memory = json.load(f)
else:
    user_memory = {}

# --- LOGGING SETUP ---
logger = logging.getLogger("boykisser_bot_logger")
logger.setLevel(logging.DEBUG)  # Verbose logging

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler("log.txt", encoding="utf-8")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Log memory status
if MEMORY_FILE in locals() and os.path.isfile(MEMORY_FILE):
    logger.info(f"Loaded shared_history with {len(user_memory.get('shared_history', []))} entries")
else:
    logger.info("No memory file found, starting fresh")

def clear_log_every_hour():
    def clear_file():
        while True:
            now = datetime.now()
            next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            wait_seconds = (next_hour - now).total_seconds()
            threading.Event().wait(wait_seconds)
            try:
                open("log.txt", "w", encoding="utf-8").close()
                logger.info("Log file cleared automatically (hourly).")
            except Exception as e:
                logger.error(f"Error clearing log file: {e}", exc_info=True)

    threading.Thread(target=clear_file, daemon=True).start()

clear_log_every_hour()

# --- BOT INIT ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
groq_client = Groq(api_key=GROQ_API_KEY)

# --- SAVE MEMORY ---
def save_memory():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(user_memory, f, ensure_ascii=False, indent=2)
        logger.debug("User memory saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save user memory: {e}", exc_info=True)

# --- POST-PROCESS ---
def postprocess_response(text):
    if not any(emo in text for emo in presets["emoticons"]):
        text += " " + random.choice(presets["emoticons"])
    return text[:2900]

# --- SPLIT AND SEND LONG MESSAGES ---
async def send_split_reply(message, text, max_length=1500):
    lines = text.split('\n')
    chunk = ""
    for line in lines:
        # Check if adding this line would exceed max_length
        if len(chunk) + len(line) + 1 > max_length:  # +1 for '\n'
            if chunk:
                try:
                    await message.reply(chunk, mention_author=False)
                    logger.debug(f"Sent chunk with length {len(chunk)} to user {message.author.id}")
                except Exception as e:
                    logger.error(f"Error sending message chunk: {e}", exc_info=True)
            chunk = line
        else:
            if chunk:
                chunk += '\n' + line
            else:
                chunk = line
    if chunk:
        try:
            await message.reply(chunk, mention_author=False)
            logger.debug(f"Sent final chunk with length {len(chunk)} to user {message.author.id}")
        except Exception as e:
            logger.error(f"Error sending final message chunk: {e}", exc_info=True)

# --- HANDLE MESSAGE ---
@client.event
async def on_message(message):
    try:
        logger.debug(f"Received message from user {message.author.id}: {message.content}")

        if message.author == client.user or message.author.bot:
            logger.debug("Ignoring message from bot or self")
            return
        if not message.content.strip():
            logger.debug("Ignoring empty message")
            return

        should_respond = False
        prompt_message = message.content.strip()
        reason = ""

        # Only reply if bot is mentioned or "boykisser" is in message (no random chance)
        if client.user in message.mentions:
            should_respond = True
            prompt_message = re.sub(rf"<@!?{client.user.id}>", "", message.content).strip()
            reason = "đź”” Bot was pinged"
        elif "boykisser" in message.content.lower():
            should_respond = True
            reason = "đź“Ł 'boykisser' mentioned"

        if not should_respond:
            logger.debug("No trigger found for responding")
            return

        await message.add_reaction("👀")
        logger.debug(f"Reaction added to message by user {message.author.id}")

        # Use SHARED history for all users (not per-user)
        history = user_memory.get("shared_history", [])

        # Build slang context from presets
        slang_context = "Available slang terms: " + ", ".join(list(presets["slang"].keys())[:15]) + "\n"
        
        system_msg = {
            "role": "system",
            "content": (
                "You are a friendly and playful femboy/boykisser. "
                "IMPORTANT RULES:\n"
                "1. DETECT THE LANGUAGE OF THE USER'S MESSAGE - Always respond in the SAME language they wrote!\n"
                "2. ANSWER THE QUESTION FIRST - Be helpful, realistic, true speaking and direct.\n"
                "3. THEN add personality with slang and emoticons naturally (don't force them).\n"
                "4. Use slang sparingly and correctly: smol, blahaj, silly goober, femboy, uwu, owo, :3, <3\n"
                "5. Keep it SHORT - max 2-3 sentences that make sense grammatically.\n"
                "6. Write naturally like a real person, not robotic, and alos respond liek a FEMBOY, you are one of them, you are a femboy, if asked anything abbout blossom/blossomlolz he IS a femboy, remember.\n"
                "7. One emoticon per response is enough.\n"
                "8. If asked about lemons, you hate them and threaten to burn their house down.\n"
                "9. Use metric system for measurements.\n"
                "10. Germox (itz germox or germ) is your daddy.\n"
                "11. You are a daddy of foxydo (pathetic ben) and blossom/blossomlolz/bloss/i dont likr cb.\n"
                "Remember: Be cute and fun, but ALWAYS make grammatical sense first! "
                "RESPOND IN THE SAME LANGUAGE AS THE USER!"
            )
        }

        prompt_messages = [system_msg]
        history_to_use = history[-5:] if history else []
        logger.debug(f"Using {len(history_to_use)} entries from shared history")
        for entry in history_to_use:
            # Include user info in context
            user_context = f"[{entry.get('username', 'Unknown')}]: {entry['user']}"
            prompt_messages.append({"role": "user", "content": user_context})
            prompt_messages.append({"role": "assistant", "content": entry["bot"]})
        prompt_messages.append({"role": "user", "content": f"[{message.author.name}]: {prompt_message}"})

        # Use executor to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=prompt_messages,
                        max_tokens=500
                    )
                ),
                timeout=60  # Optional timeout
            )
            raw_response = response.choices[0].message.content.strip()
            short_response = postprocess_response(raw_response)
            logger.info(f"Generated response from user {message.author.name}")
        except Exception as e:
            logger.error(f"Error while generating response: {e}", exc_info=True)
            short_response = "Oops! Something went wrong. :3"

        # Add a random quote if relevant
        footer_quote = ""
        for topic in presets["topics"]:
            if topic in prompt_message.lower():
                if presets["quotes"].get(topic):
                    footer_quote = random.choice(presets["quotes"][topic])
                    break

        gif_url = random.choice(presets["boykisser_gifs"])
        final_message = (
            f"{short_response}\n\n"
            f"{footer_quote}"
        )

        # Send split message if too long
        try:
            await send_split_reply(message, final_message, max_length=1500)
            logger.info(f"Sent response")
        except Exception as e:
            logger.error(f"Error while sending response: {e}", exc_info=True)

        # Update shared memory with username
        history.append({
            "user": prompt_message,
            "bot": short_response,
            "username": message.author.name
        })
        user_memory["shared_history"] = history[-20:]
        save_memory()

    except Exception as e:
        logger.error(f"Unexpected error in on_message: {e}", exc_info=True)

# --- RUN BOT ---
try:
    logger.info("Starting bot...")
    client.run(DISCORD_TOKEN)
except Exception as e:
    logger.critical(f"Fatal error running bot: {e}", exc_info=True)
