"""
MIT License

Copyright (c) 2019-Current PythonistaGuild, EvieePy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import discord
from discord.ext import commands
import logging
from typing import cast
import wavelink
from discord import app_commands

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot= bot

    class MusicGroup(app_commands.Group):
        @app_commands.command(description="Riproduci le tue canzoni preferite da vari siti (Spotify, Soundcloud, Youtube..)")
        async def play(self, interaction: discord.Interaction, *, query: str) -> None:
            """Play a song with the given query."""
            if not interaction.guild:
                return

            player: wavelink.Player
            player = cast(wavelink.Player, ctx.voice_client)  # type: ignore

            if not player:
                try:
                    player = await ctx.author.voice.channel.connect(cls=wavelink.Player)  # type: ignore
                except AttributeError:
                    await interaction.response.send_message("Please join a voice channel first before using this command.", ephemeral=True)
                    return
                except discord.ClientException:
                    await interaction.response.send_message("I was unable to join this voice channel. Please try again.", ephemeral=True)
                    return

            # Turn on AutoPlay to enabled mode.
            # enabled = AutoPlay will play songs for us and fetch recommendations...
            # partial = AutoPlay will play songs for us, but WILL NOT fetch recommendations...
            # disabled = AutoPlay will do nothing...
            player.autoplay = wavelink.AutoPlayMode.enabled

            # Lock the player to this channel...
            if not hasattr(player, "home"):
                player.home = interaction.channel
            elif player.home != interaction.channel:
                await interaction.response.send_message(f"You can only play songs in {player.home.mention}, as the player has already started there.", ephemeral=True)
                return

            # This will handle fetching Tracks and Playlists...
            # Seed the doc strings for more information on this method...
            # If spotify is enabled via LavaSrc, this will automatically fetch Spotify tracks if you pass a URL...
            # Defaults to YouTube for non URL based queries...
            tracks: wavelink.Search = await wavelink.Playable.search(query)
            if not tracks:
                await interaction.response.send_message(f"{interaction.author.mention} - Could not find any tracks with that query. Please try again.", ephemeral=True)
                return

            if isinstance(tracks, wavelink.Playlist):
                # tracks is a playlist...
                added: int = await player.queue.put_wait(tracks)
                await interaction.response.send_message(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.")
            else:
                track: wavelink.Playable = tracks[0]
                await player.queue.put_wait(track)
                await interaction.response.send_message(f"Added **`{track}`** to the queue.")

            if not player.playing:
                # Play now since we aren't playing anything...
                await player.play(player.queue.get(), volume=30)

            # Optionally delete the invokers message...
            try:
                await interaction.message.delete()
            except discord.HTTPException:
                pass


        @app_commands.command(description="Passa alla prossima canzone in playlist :)")
        async def skip(self, interaction: discord.Interaction) -> None:
            """Skip the current song."""
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player:
                return

            await player.skip(force=True)
            await interaction.message.add_reaction("\u2705")


        @app_commands.command(description="Applica il filtro nightcore alla canzone attuale")
        async def nightcore(self, interaction: discord.Interaction) -> None:
            """Set the filter to a nightcore style."""
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player:
                return

            filters: wavelink.Filters = player.filters
            filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
            await player.set_filters(filters)

            await interaction.message.add_reaction("\u2705")


        @app_commands.command(description="Stoppa o riprendi la riproduzione corrente")
        async def toggle(self, interaction: discord.Interaction) -> None:
            """Pause or Resume the Player depending on its current state."""
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player:
                return

            await player.pause(not player.paused)
            await interaction.message.add_reaction("\u2705")


        @app_commands.command(description="Alza o abbassa il volume della canzone")
        async def volume(self, interaction: discord.Interaction, value: int) -> None:
            """Change the volume of the player."""
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player:
                return

            await player.set_volume(value)
            await interaction.message.add_reaction("\u2705")


        @app_commands.command(description="Disconnetti il bot dalla vocale")
        async def disconnect(self, interaction: discord.Interaction) -> None:
            """Disconnect the Player."""
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player:
                return

            await player.disconnect()
            await interaction.message.add_reaction("\u2705")


async def setup(bot: commands.Bot):
    bot.tree.add_command(Music.MusicGroup(name="music"))
    await bot.add_cog(Music(bot))