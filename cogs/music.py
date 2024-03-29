import discord
from discord.ext import commands
import logging
from typing import cast
import wavelink
from discord import app_commands
import datetime
import typing
from pagination import Pagination
import settings
import asyncio

log = logging.getLogger("discord")

class SendMessage():

    async def as_followup_interaction(interaction: discord.Interaction, content: str | discord.Embed, eph = True):
        try:
            await interaction.followup.send(content=content, ephemeral=eph)
        except discord.NotFound as exception:
            return log.exception(exception)
    
class Music(commands.Cog):

    def __init__(self, bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_wavelink_websocket_closed(self, payload: wavelink.WebsocketClosedEventPayload):
        player: wavelink.Player | None = payload.player
        if player:
            await player.disconnect()
            log.debug(f"{payload.player.node.identifier} Websocket Chiuso ({payload.code.name})")
        log.debug(f"{payload.code.value} Websocket Chiuso ({payload.code.name})")
        
    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, node: wavelink.Node, disconnected: list[wavelink.Player]):
        for player in disconnected:
            try:
                await player.disconnect()
                log.debug(f"Disconnesso {node} (Player: {player}) in: {player.guild.name} ({player.guild.id}) - Players: {len(node.players)}")
            except Exception as exception:
                log.exception(exception)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        log.debug(f"Wavelink Node connected: {payload.node!r} | Resumed: {payload.resumed}")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            # Handle edge cases...
            return

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track

        embed: discord.Embed = discord.Embed(description=await self.bot.rcm(command="play", event_to_call="track_start", player=player, track=track), color=0xffc0cb)

        if track.artwork:
            embed.set_author(name=f"⇾ {track.author} ⇽", icon_url=f"{track.artwork}")
        else:
            embed.set_author(name=f"⇾ {track.author} ⇽")

        await player.home.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        await player.channel.send(await self.bot.rcm(command="play", event_to_call="track_start"))
        await player.disconnect()

        
    @app_commands.command(description="Riproduci le tue canzoni preferite da vari siti (Spotify, Soundcloud, Youtube..)")
    async def play(self, interaction: discord.Interaction, titolo_o_link: str) -> None:
        """Play a song with the given query."""
        await interaction.response.defer()
        if not interaction.guild:
            return

        player: wavelink.Player
        player = cast(wavelink.Player, interaction.guild.voice_client)  # type: ignore

        premade_queries = {
            "lofi": "https://open.spotify.com/playlist/37i9dQZF1DWYoYGBbGKurt?si=aa20720238d343a1",
            "tekno": "https://open.spotify.com/playlist/4LVUmDINyVZUyZwG46SfWV?si=ef888ec515754d58",
            "house": "https://open.spotify.com/playlist/37i9dQZF1EQpoj8u9Hn81e?si=2e4104b08a1c415b",
            "dubstep": "https://open.spotify.com/playlist/4YZNKPS9bM3xv1UF4WZil0?si=59d17e493ef943c8",
            "rap (americano)": "https://open.spotify.com/playlist/58O4zjTwATYSep8TYSZTr0?si=305700416e004d5f",
            "rap (italiano)": "https://open.spotify.com/playlist/44IU4j4hQ8fB5cCEmSig1E?si=015542996bc84ce9",
            "psytrance": "https://open.spotify.com/playlist/0R29couUMdcX6JUDGFFapa?si=17760d56a45d4d85"
        }
        
        if titolo_o_link.lower() in premade_queries:
            titolo_o_link = premade_queries[titolo_o_link.lower()]

        if not player:
            try:
                player = await interaction.user.voice.channel.connect(cls=wavelink.Player, self_mute=False, self_deaf=True)  # type: ignore
            except AttributeError:
                await SendMessage.as_followup_interaction(interaction=interaction, content=await interaction.client.rcm(command="play", event_to_call="AttributeError", player=player, track=track))
                return
            except discord.ClientException:
                await SendMessage.as_followup_interaction(interaction=interaction, content=await interaction.client.rcm(command="play", event_to_call="discord.ClientException", player=player, track=track))
                return

        player.autoplay = wavelink.AutoPlayMode.partial

        if not hasattr(player, "home"):
            player.home = interaction.channel
        elif player.home != interaction.channel:
            await SendMessage.as_followup_interaction(interaction=interaction, content=await interaction.client.rcm(command="play", event_to_call="interaction.channel_error", player=player, track=track))
            return

        tracks: wavelink.Search = await wavelink.Playable.search(titolo_o_link)
        if not tracks:
            await SendMessage.as_followup_interaction(interaction=interaction, content=await interaction.client.rcm(command="play", event_to_call="no_results", player=player, track=track))
            return

        if isinstance(tracks, wavelink.Playlist):
            for track in tracks:
                track.extras = {"requester": interaction.user.mention}
            added: int = await player.queue.put_wait(tracks)
            await SendMessage.as_followup_interaction(interaction=interaction, content=await interaction.client.rcm(command="play", event_to_call="added_playlist", player=player, track=track, added_tracks=added), eph=False)
        else:
            track: wavelink.Playable = tracks[0]
            track.extras = {"requester": interaction.user.mention}
            await player.queue.put_wait(track)
            await SendMessage.as_followup_interaction(interaction=interaction, content=await interaction.client.rcm(command="play", event_to_call="added_song", player=player, track=track), eph=False)

        if not player.playing:
            await player.play(player.queue.get(), volume=100)

    @play.autocomplete("titolo_o_link")
    async def play_auto(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        data = []
        for option in ["tekno", "lofi", "house", "dubstep", "rap (americano)", "rap (italiano)", "psytrance"]:
            if current.lower() in option.lower():
                data.append(app_commands.Choice(name=option.upper(), value=option.upper()))
        return data

    @app_commands.command(description="Passa alla prossima canzone in playlist :)")
    async def skip(self, interaction: discord.Interaction) -> None:
        """Skip the current song."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return

        await player.skip(force=True)
        await interaction.response.send_message(await interaction.client.rcm(command="skip", event_to_call="message", player=player, track=player.current, interaction=interaction))
    
    @app_commands.command(description="Applica un filtro alla canzone attuale!")
    async def filtro(self, interaction: discord.Interaction, nome_filtro: str) -> None:
        """Set the filter to a karaoke style."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return
        
        valid_filters = [
            "boost",
            "tremolo",
            "vibrato",
            "8d",
            "distortion",
            "nightcore"
        ]
        
        if nome_filtro.lower() in valid_filters:
            
            filters: wavelink.Filters = player.filters
            filters.reset()
            await player.set_filters(filters)
            
            if nome_filtro.lower() == "tremolo":
                filters.tremolo.set(frequency=1.0)

            elif nome_filtro.lower() == "nightcore":
                filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
                
            elif nome_filtro.lower() == "boost":
                filters.equalizer.set(bands=[{
                    "band":1,
                    "gain": 0.25
                }])
                
            elif nome_filtro.lower() == "vibrato":
                filters.vibrato.set(frequency=5)
                
            elif nome_filtro.lower() == "8d":
                filters.rotation.set(rotation_hz=0.4)
                
            elif nome_filtro.lower() == "distortion":
                filters.distortion.set(sin_offset=0.2, sin_scale=0.9, cos_offset=0.4, cos_scale=0.7, tan_offset=0.8, tan_scale=0.3, offset=0.6, scale=2.7)
                
            await player.set_filters(filters)
            await interaction.response.send_message(await interaction.client.rcm(command="filtro", event_to_call="message", player=player, track=player.current, interaction=interaction, nome_filtro=nome_filtro))
    
    @filtro.autocomplete("nome_filtro")
    async def filtro_auto(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        data = []
        for valid_filters in ["boost","tremolo","vibrato","8d","distortion","nightcore"]:
            if current.lower() in valid_filters.lower():
                data.append(app_commands.Choice(name=valid_filters.upper(), value=valid_filters.upper()))
        return data
        
    
    @app_commands.command(description="Disabilita i filtri applicati (se presenti)")
    async def nofiltri(self, interaction: discord.Interaction) -> None:
        """Set the filter to a nightcore style."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return
        
        filters: wavelink.Filters = player.filters

        if filters:
            filters.reset()
            await player.set_filters(filters)
            await interaction.response.send_message(await interaction.client.rcm(command="nofiltro", event_to_call="message1", player=player, track=player.current, interaction=interaction))
        else:
            await interaction.response.send_message(await interaction.client.rcm(command="nofiltro", event_to_call="message2", player=player, track=player.current, interaction=interaction))


    @app_commands.command(description="Stoppa o riprendi la riproduzione corrente")
    async def toggle(self, interaction: discord.Interaction) -> None:
        """Pause or Resume the Player depending on its current state."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return

        await player.pause(not player.paused)
        await interaction.response.send_message(await interaction.client.rcm(command="toggle", event_to_call="message", player=player, track=player.current, interaction=interaction))

    @app_commands.command(description="Alza o abbassa il volume della canzone (da 0 a 100)")
    async def volume(self, interaction: discord.Interaction, valore: int) -> None:
        """Change the volume of the player."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return

        await player.set_volume(valore)
        await interaction.response.send_message(await interaction.client.rcm(command="volume", event_to_call="message", player=player, track=player.current, interaction=interaction))


    @app_commands.command(description="Disconnetti il bot dalla vocale")
    async def stop(self, interaction: discord.Interaction) -> None:
        """Disconnect the Player."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return

        await player.disconnect()
        await interaction.response.send_message(await interaction.client.rcm(command="stop", event_to_call="message", player=player, track=player.current, interaction=interaction))
        
    @app_commands.command(description="Visualizza tutte le canzoni in coda")
    async def queue(self, interaction: discord.Interaction, svuota: typing.Optional[str]) -> None:
        """Check the queue."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return
        
        if len(player.queue) <= 1:
            return await interaction.response.send_message(await interaction.client.rcm(command="queue", event_to_call="no_queue", player=player, track=player.current, interaction=interaction))
        
        if svuota:
            if svuota.lower() == "svuota la queue.":
                player.queue.clear()
                return await interaction.response.send_message(await interaction.client.rcm(command="queue", event_to_call="queue_cleared", player=player, track=player.current, interaction=interaction))
        
        async def get_page(page: int):
            emb = discord.Embed(description = await interaction.client.rcm(command="queue", event_to_call="queue_embed_desc", player=player, track=player.current, interaction=interaction), color=0xffc0cb)
            offset = (page-1) * settings.MAX_EMBED_LENGHT
            
            index = 0
            
            for item in player.queue[offset: offset+settings.MAX_EMBED_LENGHT]:
                seconds = item.length/1000
                b = int((seconds % 3600)//60)
                c = int((seconds % 3600) % 60)
                dt = datetime.time(0, b, c)
                index = index + 1
                emb.description += f"**`{index}`**) **{item.author}** ↪ {item.extras.requester}\n- [{item.title}]({item.uri}) | `{dt.strftime('%M:%S')}`\n\n"
                
            emb.set_author(name=f"{interaction.guild.name}" + await interaction.client.rcm(command="queue", event_to_call="music_word", player=player, track=player.current, interaction=interaction), icon_url=interaction.guild.icon.url)
            n = Pagination.compute_total_pages(len(player.queue), settings.MAX_EMBED_LENGHT)
            emb.set_footer(text=await interaction.client.rcm(command="queue", event_to_call="page_word", player=player, track=player.current, interaction=interaction) + f" {page}/{n}")
            return emb, n

        await Pagination(interaction, get_page).navegate()

    @queue.autocomplete("svuota")
    async def queue_auto(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        data = []
        for option in ["Svuota la queue.", "Non svuotare la queue."]:
            if current.lower() in option.lower():
                data.append(app_commands.Choice(name=option.upper(), value=option.upper()))
        return data


async def setup(bot: commands.Bot):
    m_bot = Music(bot)
    await bot.add_cog(Music(bot))