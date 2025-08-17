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
from together import Together

# --- ENV LOAD ---
load_dotenv(dotenv_path=".env.kiss")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

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
together_client = Together(api_key=TOGETHER_API_KEY)

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
            reason = "🔔 Bot was pinged"
        elif "boykisser" in message.content.lower():
            should_respond = True
            reason = "📣 'boykisser' mentioned"

        if not should_respond:
            logger.debug("No trigger found for responding")
            return

        await message.add_reaction("⏰")
        logger.debug(f"Reaction '⏰' added to message by user {message.author.id}")

        user_id = str(message.author.id)
        history = user_memory.get(user_id, [])

        system_msg = {
            "role": "system",
            "content": (
                "You are a friendly, playful, and chaotic femboy/boykisser Discord bot. "
                "You use furry/femboy/boykisser slang, emoticons, and memes from the modern queer internet. "
                "Always be silly, cute, and welcoming. Use the slang dictionary and example quotes from "
                "slang_presets.json in your replies. Always include at least one emoticon per message. "
                "Reply with short, meme-y, authentic femboy/boykisser responses. No long paragraphs or lectures."
                "If asked any calculations use the metric system."
            )
        }

        prompt_messages = [system_msg]
        for entry in history[-5:]:
            prompt_messages.append({"role": "user", "content": entry["user"]})
            prompt_messages.append({"role": "assistant", "content": entry["bot"]})
        prompt_messages.append({"role": "user", "content": prompt_message})

        # Use executor to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: together_client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
                        messages=prompt_messages
                    )
                ),
                timeout=60  # Optional timeout
            )
            raw_response = response.choices[0].message.content.strip()
            clean_response = re.sub(r"<think>.*?</think>", "", raw_response, flags=re.DOTALL).strip()
            short_response = postprocess_response(clean_response)
            logger.info(f"Generated response for user {user_id}")
        except Exception as e:
            logger.error(f"Error while generating response for user {user_id}: {e}", exc_info=True)
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
            f"{footer_quote}\n"
            f"🤔 **BOYKISSER SPOTTED!** {random.choice(presets['emoticons'])}\n"
            f"{gif_url}"
        )

        # Send split message if too long
        try:
            await send_split_reply(message, final_message, max_length=1500)
            logger.info(f"Sent response to user {user_id}")
        except Exception as e:
            logger.error(f"Error while sending response to user {user_id}: {e}", exc_info=True)

        # Update memory
        history.append({"user": prompt_message, "bot": short_response})
        user_memory[user_id] = history[-10:]
        save_memory()

    except Exception as e:
        logger.error(f"Unexpected error in on_message: {e}", exc_info=True)

# --- RUN BOT ---
try:
    logger.info("Starting bot...")
    client.run(DISCORD_TOKEN)
except Exception as e:
    logger.critical(f"Fatal error running bot: {e}", exc_info=True)
