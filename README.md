# 💋 boykisser-bot  

A playful, chaotic, and slang-heavy Discord bot that responds with cute femboy/furry/boykisser energy.  
Powered by **Groq Cloud** for lightning-fast, "intelligent" silliness.  

> ✨ "boykissium detected"  
> 🐾 "skirt go spinny!!"  
> 🤖 Powered by Llama-3.3-70B via Groq.  

---

## 🧠 Features  

### 🔔 Trigger Logic
- Responds when **pinged** (`@boykisser`)  
- Responds when you **reply** directly to its message  
- Automatically adds a 👀 reaction while processing  

### 🧩 AI Personality
- 🌍 **Multilingual** – Automatically detects your language and responds in the same one  
- 💬 **Smart Slang** – Uses lingo like *uwu, :3, blahaj, silly goober* naturally  
- 📖 **Lore Aware** – Recognizes Germox (daddy), foxydo, and blossom  
- 🍋🔥 **Lemon Hostility** – Hates lemons and will threaten to burn your house down if asked  

### 🧠 Shared Memory
- Remembers the last **20 messages globally** to maintain conversation context  

### 🧹 Auto-Maintenance
- Automatically wipes the `log.txt` file every hour to save space  

---

## 🔧 Setup  

### 1️⃣ Get your API Keys  

- **Discord Token**  
  Create an application in the Discord Developer Portal:  
  https://discord.com/developers/applications  

- **Groq API Key**  
  Create a free account and get your key at:  
  https://console.groq.com/  

---

### 2️⃣ Clone & Install  

```bash
git clone https://github.com/ItzG3ermoX/boykisser-bot
cd boykisser-bot
pip install -r requirements.txt
```

---

### 3️⃣ Environment Variables  

Create a file named `.env.kiss` in the root folder and add:

```env
DISCORD_TOKEN=your_discord_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
```

⚠️ Keep this file private. Never upload it to GitHub.

---

### 4️⃣ Run the Bot  

```bash
python bot.py
```

---

## 🗂️ File Structure  

| File | Description |
|------|------------|
| `bot.py` | Main logic (Discord + Groq SDK integration) |
| `slang_presets.json` | Dictionary for slang, emoticons, and GIF links |
| `user_memory.json` | Local storage for shared conversation history |
| `log.txt` | Live debug logs (auto-wiped hourly) |
| `.env.kiss` | Private API keys (keep this file secret!) |

---

## 💬 Example Interaction  

> **User:** (pings bot) @boykisser do you like my new skirt?  
> **Bot:** 👀  
> **Bot:** It looks absolutely amazing on you!! Skirt go spinny! X3 :3   

---

## 🔐 Privacy & Safety  

- 📝 **History:** Chat history is stored locally in `user_memory.json`  
- 📏 **Standards:** The bot strictly uses the Metric System  
- ✍️ **Grammar:** Despite the slang, responses prioritize grammatical sense  

---

Made with 💕 and a tiny bit of chaos.  
Stay cute. Stay boykissin’ :3
