import discord
import random
import re
import json
import os
import asyncio
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

# --- BOT INIT ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
together_client = Together(api_key=TOGETHER_API_KEY)

# --- SAVE MEMORY ---
def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(user_memory, f, ensure_ascii=False, indent=2)

# --- POST-PROCESS ---
def postprocess_response(text):
    if not any(emo in text for emo in presets["emoticons"]):
        text += " " + random.choice(presets["emoticons"])
    return text[:2900]

# --- HANDLE MESSAGE ---
@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return
    if not message.content.strip():
        return

    should_respond = False
    prompt_message = message.content.strip()
    reason = ""

    if client.user in message.mentions:
        should_respond = True
        prompt_message = re.sub(rf"<@!?{client.user.id}>", "", message.content).strip()
        reason = "🔔 Bot was pinged"
    elif "boykisser" in message.content.lower():
        should_respond = True
        reason = "📣 'boykisser' mentioned"
    elif random.randint(1, 20) == 1:
        should_respond = True
        reason = "🎲 Random chance (1 in 20)"

    if not should_respond:
        return

    await message.add_reaction("⏰")

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
            timeout=20  # Optional timeout
        )
        raw_response = response.choices[0].message.content.strip()
        clean_response = re.sub(r"<think>.*?</think>", "", raw_response, flags=re.DOTALL).strip()
        short_response = postprocess_response(clean_response)
    except Exception as e:
        print(f"Error while generating response: {e}")
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
    if len(final_message) > 4000:
        final_message = final_message[:3997] + "..."

    await message.reply(final_message, mention_author=False)

    # Update memory
    history.append({"user": prompt_message, "bot": short_response})
    user_memory[user_id] = history[-10:]
    save_memory()

# --- RUN BOT ---
client.run(DISCORD_TOKEN)
