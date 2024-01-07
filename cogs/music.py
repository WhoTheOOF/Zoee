import discord
from discord.ext import commands
import logging
from typing import cast
import wavelink
from discord import app_commands
import time
import datetime
import typing
from pagination import Pagination
import settings

class Music(commands.Cog):

    async def setup(self):
        nodes = [wavelink.Node(uri="http://lavalink.jirayu.pw:2333", password="youshallnotpass")]
        await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=None)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        logging.info(f"Wavelink Node connected: {payload.node!r} | Resumed: {payload.resumed}")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            # Handle edge cases...
            return

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track

        seconds = track.length/1000
        b = int((seconds % 3600)//60)
        c = int((seconds % 3600) % 60)
        dt = datetime.time(0, b, c)

        embed: discord.Embed = discord.Embed(description=f"<a:hellokittyexcited:1193494992967180381> Riproducendo **[{track.title}]({track.uri}) (`{dt.strftime('%M:%S')}`)** ({track.extras.requester if track.extras.requester else 'Anonimo'})", color=0xffc0cb)
        embed.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}", icon_url=player.guild.icon.url)

        if track.artwork:
            embed.set_author(name=f"⇾ {track.author} ⇽", icon_url=f"{track.artwork}")
        else:
            embed.set_author(name=f"⇾ {track.author} ⇽")

        if original and original.recommended:
            embed.description += f"\n\n`Questa canzone e' stata raccomandata da **`{track.source}`**"

        await player.home.send(embed=embed)

    def __init__(self, bot):
        self.bot= bot

    class MusicGroup(app_commands.Group):
        
        @app_commands.command(description="Riproduci le tue canzoni preferite da vari siti (Spotify, Soundcloud, Youtube..)")
        async def play(self, interaction: discord.Interaction, titolo_o_link: str) -> None:
            """Play a song with the given query."""
            if not interaction.guild:
                return

            player: wavelink.Player
            player = cast(wavelink.Player, interaction.guild.voice_client)  # type: ignore

            if not player:
                try:
                    player = await interaction.user.voice.channel.connect(cls=wavelink.Player)  # type: ignore
                except AttributeError:
                    await interaction.response.send_message("<a:hellokittyangry:1193495024437047346> Entra in un canale vocale prima di usare questo comando.", ephemeral=True)
                    return
                except discord.ClientException:
                    await interaction.response.send_message("<a:hellokittyangry:1193495024437047346> Non ho i permessi per entrare nel canale vocale.", ephemeral=True)
                    return

            # Turn on AutoPlay to enabled mode.
            # enabled = AutoPlay will play songs for us and fetch recommendations...
            # partial = AutoPlay will play songs for us, but WILL NOT fetch recommendations...
            # disabled = AutoPlay will do nothing...
            player.autoplay = wavelink.AutoPlayMode.partial

            # Lock the player to this channel...
            if not hasattr(player, "home"):
                player.home = interaction.channel
            elif player.home != interaction.channel:
                await interaction.response.send_message(f"<a:hellokittyangry:1193495024437047346> Puoi usare questo comando solo in {player.home.mention}, non posso essere in piu' vocali contemporaneamente.", ephemeral=True)
                return

            # This will handle fetching Tracks and Playlists...
            # Seed the doc strings for more information on this method...
            # If spotify is enabled via LavaSrc, this will automatically fetch Spotify tracks if you pass a URL...
            # Defaults to YouTube for non URL based queries...
            tracks: wavelink.Search = await wavelink.Playable.search(titolo_o_link)
            if not tracks:
                await interaction.response.send_message(f"<a:hellokittyangry:1193495024437047346> Non ho trovato nessun risultato per **`{titolo_o_link}`**, riprova.", ephemeral=True)
                return

            if isinstance(tracks, wavelink.Playlist):
                # tracks is a playlist...
                for track in tracks:
                    track.extras = {"requester": interaction.user.mention}
                added: int = await player.queue.put_wait(tracks)
                await interaction.response.send_message(f"<a:hellokittywave:1193495028874608773> Aggiunta la playlist **[{tracks.name}]({tracks.url})** ({added} traccie) alla coda.")
            else:
                track: wavelink.Playable = tracks[0]
                track.extras = {"requester": interaction.user.mention}
                await player.queue.put_wait(track)
                await interaction.response.send_message(f"<a:hellokittywave:1193495028874608773> **`{track}`** è stata aggiunta alla coda delle canzoni.")

            if not player.playing:
                # Play now since we aren't playing anything...
                await player.play(player.queue.get(), volume=100)

        @app_commands.command(description="Passa alla prossima canzone in playlist :)")
        async def skip(self, interaction: discord.Interaction) -> None:
            """Skip the current song."""
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player:
                return

            await player.skip(force=True)
            await interaction.response.send_message(f"<a:8319hellokittyno:1193495006170861588> {interaction.user.mention} ha skippato la traccia attuale.")
        
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
                    filters.distortion.set(sin_offset=0.2, sin_scale=0.9, cos_offset=0.4, cos_scale=0.7, tan_offset=1.8, tan_scale=1.3, offset=0.6, scale=2.7)
                    
                await player.set_filters(filters)
                await interaction.response.send_message(f"<a:8319hellokittyno:1193495006170861588> {interaction.user.mention} ha impostato il filtro **`{nome_filtro.upper()}`**.")
        
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
                await interaction.response.send_message(f"<a:8319hellokittyno:1193495006170861588> {interaction.user.mention} ha rimosso i filtri applicati alla canzone.")
            else:
                await interaction.response.send_message(f"<a:8319hellokittyno:1193495006170861588> {interaction.user.mention} Non ci sono filtri applicati da rimuovere.")


        @app_commands.command(description="Stoppa o riprendi la riproduzione corrente")
        async def toggle(self, interaction: discord.Interaction) -> None:
            """Pause or Resume the Player depending on its current state."""
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player:
                return

            await player.pause(not player.paused)
            await interaction.response.send_message(f"<a:8319hellokittyno:1193495006170861588> {interaction.user.mention} ha messo in pausa.")

        @app_commands.command(description="Alza o abbassa il volume della canzone (da 0 a 100)")
        async def volume(self, interaction: discord.Interaction, valore: int) -> None:
            """Change the volume of the player."""
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player:
                return

            await player.set_volume(valore)
            await interaction.response.send_message(f"<a:8319hellokittyno:1193495006170861588> {interaction.user.mention} ha modificato il volume a **`{player.volume}/100`**.")



        @app_commands.command(description="Disconnetti il bot dalla vocale")
        async def stop(self, interaction: discord.Interaction) -> None:
            """Disconnect the Player."""
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player:
                return

            await player.disconnect()
            await interaction.response.send_message(f"<a:8319hellokittyno:1193495006170861588> {interaction.user.mention} ha disconnesso il bot.")
            
        @app_commands.command(description="Visualizza tutte le canzoni in coda")
        async def queue(self, interaction: discord.Interaction, svuota: typing.Optional[str]) -> None:
            """Check the queue."""
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player:
                return
            
            if len(player.queue) <= 1:
                return await interaction.response.send_message(f"<a:8319hellokittyno:1193495006170861588> E' presente solo una canzone al momento, che e' quella corrente.")
            
            if svuota:
                if svuota.lower() == "svuota la queue.":
                    player.queue.clear()
                    return await interaction.response.send_message(f"<a:8319hellokittyno:1193495006170861588> {interaction.user.mention} ha svuotato la queue.")
            
            async def get_page(page: int):
                emb = discord.Embed(description = f"# <a:hellokittyshake:1193495018078482512> CODA CANZONI <a:hellokittyshake:1193495018078482512> # \n", color=0xffc0cb)
                offset = (page-1) * settings.MAX_EMBED_LENGHT
                
                index = 0
                
                for item in player.queue[offset: offset+settings.MAX_EMBED_LENGHT]:
                    seconds = item.length/1000
                    b = int((seconds % 3600)//60)
                    c = int((seconds % 3600) % 60)
                    dt = datetime.time(0, b, c)
                    index = index + 1
                    emb.description += f"**`{index}`**) **{item.author}** ↪ Da: {item.extras.requester}\n- [{item.title}]({item.uri}) | `{dt.strftime('%M:%S')}`\n\n"
                    
                emb.set_author(name=f"{interaction.guild.name} Musica", icon_url=interaction.guild.icon.url)
                n = Pagination.compute_total_pages(len(player.queue), settings.MAX_EMBED_LENGHT)
                emb.set_footer(text=f"Pagina {page}/{n}")
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
    bot.tree.add_command(Music.MusicGroup(name="music"))
    await bot.add_cog(Music(bot))
    await m_bot.setup()