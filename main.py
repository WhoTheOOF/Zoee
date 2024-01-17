import discord
from discord.ext import commands, tasks, ipc
import settings
import os
import logging
from typing import cast
from discord.ext.ipc.server import Server
from discord.ext.ipc.objects import ClientPayload
import asyncio
from utils.functions import StaffAppButtons, BottoneNone
import wavelink
import logging.handlers
import typing
import asyncpg
import json
import datetime

log = logging.getLogger("discord")

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

class Zoee(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        intents.message_content = True

        super().__init__(
            command_prefix=["zoe ", "z!"], 
            intents=intents
        )

        self.ipc = ipc.Server(self, secret_key="Zoee")
        self.pool: asyncpg.Pool = None
        self.translations: dict = {}
        self.server_languages: dict = {}
        self.wavelink: wavelink.Player = None

    def gslt(self, server_id: int):
        current = self.server_languages[server_id]
        if current:
            return self.translations[current]
        return None

    async def reformat_message(self, m: str, 
                               query = None, 
                               interaction: discord.Interaction = None, 
                               added_tracks = None, player: wavelink.Player = None, 
                               track: wavelink.Playable = None,
                               nome_filtro = None) -> str:
        """
        Simple helper function to reformat some variables
        into their correct value, returning the formatted message.
        """
        
        if track:
            seconds = track.length/1000
            b = int((seconds % 3600)//60)
            c = int((seconds % 3600) % 60)
            dt = datetime.time(0, b, c)
        
        namespace = {
            "{track.title}": track.title,
            "{track.uri}": track.uri,
            "{track.extras.requester}": track.extras.requester if track.extras.requester else '???',
            "{dt.strftime('%M:%S')}": dt.strftime('%M:%S'),
            "{track.author}": track.author,
            "{player.home.mention}": player.home.mention if player else "???",
            "{titolo_o_link}": query,
            "{added}": added_tracks,
            "{track}": track,
            "{tracks.name}": track.title,
            "{tracks.url}": track.uri,
            "{interaction.user.mention}": interaction.user.mention,
            "{nome_filtro.upper()}": nome_filtro
        }
        
        for k in namespace.keys():
            m = m.replace(k, str(namespace[k]))
        return m

    async def setup_hook(self):
        
        # Start the IPC server.
        await self.ipc.start()
        log.info("[IPC] IPC Server Started")
        
        # Connects to the Lavalink Server configured.
        nodes = [wavelink.Node(uri=settings.LAVALINK_INFO['server'], password=settings.LAVALINK_INFO['password'], inactive_player_timeout=300)]
        s = await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=None)
        self.wavelink = s
        log.info(f"Connesso a Lavalink: {s}")
        
        # Connects to the Database configured.
        self.pool = await asyncpg.create_pool(settings.DATABASE_URL)
        log.info(f"Database Connected: {self.pool}")
        
        # Cache translations
        translation = await bot.pool.fetch('SELECT * FROM translations')
        for tr in translation:
            self.translations[tr['language_name']] = json.loads(tr['translate'])
            log.info("[CACHE] Translations Cached.")
        
        # Cache server languages
        server_settings = await bot.pool.fetch("SELECT * FROM server_languages")
        for server in server_settings:
            self.server_languages[server['id']] = server['lang']
            log.info("[CACHE] Server Languages Cached.")
        
        # Loads Cogs and Utilities from corresponding folders.
        await self.load_extension("jishaku")
        for cog_file in os.listdir("./cogs"):
            if cog_file.endswith(".py"):
                await self.load_extension(f"cogs.{cog_file[:-3]}")
                log.info(f"Caricato {cog_file}.")
        
        for file in os.listdir("./utils"):
            if file.endswith('.py'):
                await self.load_extension(f"utils.{file[:-3]}")
                log.info(f"Caricato {file}.")
            
        # Resume previously made Views.
        self.add_view(StaffAppButtons())
        self.add_view(BottoneNone())

    async def async_cleanup(self):
        await self.ipc.stop()
        log.warning("[IPC] IPC Server Closed.")

    async def close(self):
        await self.async_cleanup()
        await self.pool.close()
        await super().close()

    @Server.route()
    async def get_user_data(self, data: ClientPayload) -> typing.Dict:
        user = self.get_user(data.id)
        return user._to_minimal_user_json()

    @Server.route()
    async def online_users(self, data: ClientPayload):
        online = 0
        guild = self.get_guild(1192455862464299058)
        for user in guild.members:
            if user.status == discord.Status.online:
                online += 1
        return str(online)
            

    @Server.route()
    async def total_users(self, data: ClientPayload):
        guild = self.get_guild(1192455862464299058)
        return str(len(guild.members))

    @Server.route()
    async def verified_users(self, data: ClientPayload):
        verified = 0
        guild = self.get_guild(1192455862464299058)
        r = guild.get_role(1192457209142059098)
        for user in guild.members:
            if r in user.roles:
                verified += 1
        return str(verified)

bot = Zoee()

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

if __name__ == "__main__":
    bot.run(settings.DISCORD_API_SECRET)