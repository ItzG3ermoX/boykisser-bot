# 💋 boykisser-bot

A playful, chaotic, and slang-heavy Discord bot that responds with cute femboy/furry/boykisser energy. Think memes, emoticons, and silliness—all powered by AI via [Together.ai](https://www.together.ai/).

> ✨ "boykissium detected"  
> 🐾 "skirt go spinny!!"  
> 🤖 Made for those who crave goofy vibes in their server.

---

## 🧠 Features

- Responds to:
  - Mentions (`@boykisser`)
  - The word `boykisser`
  - Random messages (1 in 20 chance)
- Always replies with:
  - Meme-like femboy slang
  - One or more emoticons (e.g. `:3`, `X3`, `owo`)
  - Optional GIF from the boykisser collection
- Personal memory per user (short-term context)
- Includes a preset-based **slang dictionary** and **quote matcher** based on message content
- GPT-style responses using Together.ai

---

## 🔧 Setup

### 1. Clone this repo

```bash
git clone https://github.com/yourusername/boykisser-bot.git
cd boykisser-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> Required packages include:  
> `discord.py`, `together`, `python-dotenv`

### 3. Add environment variables

Create a file named `.env.kiss` in the project folder and add your keys:

```env
DISCORD_TOKEN=your_discord_bot_token
TOGETHER_API_KEY=your_together_api_key
```

The discord bot token can be found in your discord developer portal.
Together.ai API can be found in your together.ai account settings under API Keys.

### 4. Run the bot

```bash
python bot.py
```

---

## 🗂️ File Structure

| File                  | Description                                       |
|-----------------------|---------------------------------------------------|
| `bot.py`              | Main bot logic (Discord + Together integration)   |
| `slang_presets.json`  | Contains slang, emoticons, GIFs, and quotes       |
| `user_memory.json`    | Stores short-term user memory                     |
| `.env.kiss`           | Secret tokens (not committed to version control)  |

---

## 💬 Example Response

> **User:** hey @boykisser what’s the vibe?  
> **Bot:** silly vibe detected :3 finally, boykissium!!  
> 🤔 **BOYKISSER SPOTTED!** X3  
> https://c.tenor.com/R54aJnNOznkAAAAC/tenor.gif

---

## 🔐 Privacy & Safety

- Messages are processed using an external AI model via Together.ai  
- No long-term memory: user history is stored locally in `user_memory.json`  
- Safe for queer, meme-heavy, chaotic spaces  
- Not designed for moderation or SFW-only use (yet)

---

## 🧪 Future Ideas

- Slash command support (e.g. `/vibe`)
- Custom model switching
- Web dashboard for editing `slang_presets.json`
- Server-specific behavior toggle (chaotic vs polite)

---

## 🧃 Bonus Quotes

> “Burschenküsser meldet sich zum Dienst :33”  
> “I gaslit one of my friends into becoming a Femboy as a joke...”  
> “Skirt go spinny!!”  
> “Finally, boykissium.”

---

Made with 💕 and just a smol pinch of chaos.  
Stay cute. Stay cursed. Stay boykissin’ :3
