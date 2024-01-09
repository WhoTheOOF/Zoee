import discord
from discord.ext import commands
import asyncio
import datetime
import typing
import logging
import os

logging.getLogger(__name__)
    
class SendMessage():

    async def as_interaction(interaction: discord.Interaction, content: str, eph: True):
        try:
            await interaction.response.defer()
            await interaction.followup.send(content=content, ephemeral=eph)
        except Exception as exception:
            return logging.error(f"✕ Errore in as_interaction (functions.py): {exception}")
    
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
                print(f"Caricato {cog_file}.")
                
    discord.utils.setup_logging(level=logging.INFO)


bot = Zoee(command_prefix=["zoe ", "z!", "<@1191841650444607588> "], intents=Zoee.intents)

class StartUp():
    def startup_bot(token):
        bot.run(token)
        
        
        
        