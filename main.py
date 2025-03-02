import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('bot')

# Load environment variables from .env file
load_dotenv()

# Bot configuration
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")
COGS_DIR = "cogs"

# Intents configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.messages = True

# Initialize the bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Using prefix: {PREFIX}")
    await load_cogs()
    
    # Debug: Print all registered commands
    logger.info("Registered commands:")
    for command in bot.commands:
        logger.info(f"- {command.name}")

async def load_cogs():
    for filename in os.listdir(COGS_DIR):
        if filename.endswith(".py"):
            cog_name = filename[:-3]  # Remove the .py extension
            try:
                await bot.load_extension(f"{COGS_DIR}.{cog_name}")
                logger.info(f"✅ Successfully loaded cog: {cog_name}")
            except Exception as e:
                logger.error(f"❌ Failed to load cog {cog_name}: {str(e)}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    logger.debug(f"Message received: {message.content}")
    logger.debug(f"Prefix check: {message.content.startswith(PREFIX)}")
    
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        logger.error(f"Command not found: {ctx.message.content}")
        await ctx.send(f"❌ Command not found. Use `{PREFIX}help` to see available commands.")
    else:
        logger.error(f"Error: {str(error)}")
        await ctx.send(f"❌ An error occurred: {str(error)}")

if __name__ == "__main__":
    if not TOKEN:
        logger.error("❌ Error: Discord bot token not found in .env file.")
    else:
        bot.run(TOKEN)