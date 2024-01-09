import discord
from discord.ext import commands
import settings
import os
from typing import Literal, Optional
import logging
from typing import cast
from discord.ext import tasks
import asyncio

log = logging.getLogger(__name__)

class Zoee(commands.Bot):
    
    intents = discord.Intents.all()
    intents.message_content = True

    os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
    os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
    os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
    
    async def setup_hook(self):
        await self.load_extension("jishaku")
        for cog_file in os.listdir("./cogs"):
            if cog_file.endswith(".py"):
                await self.load_extension(f"cogs.{cog_file[:-3]}")
                log.info(f"Caricato {cog_file}.")
        
        for file in os.listdir("./utils"):
            if file.endswith('.py'):
                await self.load_extension(f"utils.{file[:-3]}")
                log.info(f"Caricato {file}.")

bot = Zoee(command_prefix=["zoe ", "z!", "<@1191841650444607588> "], intents=Zoee.intents)

class StartUp():
    def startup_bot(token):
        bot.run(token)

@tasks.loop(seconds=10)
async def statusloop():
    await bot.wait_until_ready()
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name=f"💃 SLURP"))
    await asyncio.sleep(30)
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.playing, name=f"osu!", assets={
        "large_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Osu%21_Logo_2016.svg/2048px-Osu%21_Logo_2016.svg.png",
        "large_text": "Giocando osu con amici!"
        }))
    await asyncio.sleep(30)

@bot.event
async def on_ready():
    log.info(f'Loggato come {bot.user}!')
    await statusloop.start()

StartUp.startup_bot(token=settings.DISCORD_API_SECRET)