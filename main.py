import asyncio
import discord
from discord.ext import commands
import os
from config import TOKEN, PREFIX

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None, case_insensitive=True)

async def load():
    """
    Loads all the cogs in the cogs folder
    """
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            # removes the .py extension
            await bot.load_extension(f'cogs.{file[:-3]}')

async def main():
    await load()
    await bot.start(TOKEN)

asyncio.run(main())
