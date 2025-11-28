import os
import discord
from discord.ext import commands

# ===== DISCORD CONFIG =====
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
COMMAND_PREFIX = "!"
# ==========================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


# --- Basic example commands (optional) --- #

@bot.command(name="ping")
async def ping(ctx: commands.Context):
    await ctx.send("Pong! 🏓")


@bot.command(name="hello")
async def hello(ctx: commands.Context):
    await ctx.send(f"Hey {ctx.author.mention} 👋")


# --- Extension loading and startup --- #

async def main():
    if not TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN environment variable is not set.")

    # Load the Minecraft commands from minecraft.py
    await bot.load_extension("minecraft")

    # Start the bot
    await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
