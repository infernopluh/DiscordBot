import discord
from discord.ext import commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Load all cogs in the cogs directory
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and not filename.startswith("__"):
        bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run("YOUR_BOT_TOKEN")
