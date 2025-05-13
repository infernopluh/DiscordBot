# Discord Ultimate Bot

A modular Discord bot packed with tons of features!  
Features are organized in cogs (modules) for easy management.

## Setup

1. **Install requirements:**
   ```
   pip install discord.py yt-dlp
   ```

   Also install [ffmpeg](https://ffmpeg.org/) on your system and make sure it's in your PATH.

2. **Add your bot token:**  
   In `bot.py`, replace `"YOUR_BOT_TOKEN"` with your bot's token.

3. **Add or edit features:**  
   Put new commands in files inside the `cogs/` folder.  
   Each file is a "cog" (module of features).

4. **Run your bot:**  
   ```
   python bot.py
   ```

## Features

- **Moderation:** Kick, ban, mute, unmute, clear, slowmode
- **Fun:** Roll, joke, meme, coinflip, 8ball, rate
- **Utility:** Ping, uptime, reminder, poll, user/server info
- **Music:** Join, leave, play (YouTube), pause, resume, stop, skip, queue
- **Economy:** Balance, daily, give, leaderboard (persistent)
- **AI:** Ask AI, imagegen, sentiment (simulated)
- **Integrations:** GitHub, Reddit, Twitter info (simulated)

## Folder Guide

- **bot.py** — Main file, runs your bot
- **cogs/** — Put your features here!
- **data/** — Save info here (user points, etc.)
- **assets/** — Pictures, memes, sounds
- **logs/** — Log files (optional)
- **utils/** — Helper code (optional)
