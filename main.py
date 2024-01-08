import discord
from discord.ext import commands
import settings
import os
from typing import Literal, Optional
import logging
from typing import cast
from discord.ext import tasks
import asyncio

intents = discord.Intents.all()
intents.message_content = True

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

class Selene(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("jishaku")
        for cog_file in os.listdir("./cogs"):
            if cog_file.endswith(".py"):
                await self.load_extension(f"cogs.{cog_file[:-3]}")
                print(f"Caricato {cog_file}.")
                
discord.utils.setup_logging(level=logging.INFO)
selene = Selene(command_prefix="s!", intents=intents)

@tasks.loop(seconds=10)
async def statusloop():
    await selene.wait_until_ready()
    await selene.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name=f"💃 SLURP"))
    await asyncio.sleep(30)
    await selene.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.playing, name=f"osu!", assets={
        "large_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Osu%21_Logo_2016.svg/2048px-Osu%21_Logo_2016.svg.png",
        "large_text": "Giocando osu con amici!"
        }))
    await asyncio.sleep(30)

@selene.event
async def on_ready():
    print(f'Loggato come {selene.user}!')
    await statusloop.start()
    
@selene.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

if __name__ == "__main__":
    selene.run(settings.DISCORD_API_SECRET)