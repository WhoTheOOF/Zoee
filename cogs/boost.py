import discord
from discord.ext import commands
import time

class Boost(commands.Cog):

    def __init__(self, bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_message(self, message):
        
        if "MessageType.premium_guild" in str(message.type):
            db = discord.utils.get(message.guild.roles, id=1192951322350190783)
            sb = discord.utils.get(message.guild.roles, id=1192555588115247164)
            
            server_boost_embed = discord.Embed(
                description=f"# 🦋 NUOVO BOOST 🦋 #\n\n<:discordboost:1192556344159522986> Grazie mille per il boost {message.author.mention} <3\n<:3503rolemanager:1192554243861794817> Hai ricevuto il ruolo {sb.mention} ~!",
            )
            server_boost_embed.set_author(name=f"⇾ 💃 SLURP CREW Annuncio Boost ⇽", icon_url=message.guild.icon.url)
            server_boost_embed.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}", icon_url=message.guild.icon.url)
            server_boost_embed.set_thumbnail(url=message.author.icon.url)
            
            double_boost_embed = discord.Embed(
                description=f"# 🦋 NUOVO BOOST 🦋 #\n\n<:discordboost:1192556344159522986> Grazie mille per il secondo boost {message.author.mention} <3\n<:3503rolemanager:1192554243861794817> Hai ricevuto il ruolo {db.mention} ~!",
            )
            double_boost_embed.set_author(name=f"⇾ 💃 SLURP CREW Annuncio Double Boost ⇽", icon_url=message.guild.icon.url)
            double_boost_embed.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}", icon_url=message.guild.icon.url)
            double_boost_embed.set_thumbnail(url=message.author.icon.url)
            
            if "Server Booster" in message.author.roles:
                await message.author.add_roles(db)
                await message.channel.send(embed=double_boost_embed)
            else:
                await message.author.add_roles(sb)
                await message.channel.send(embed=server_boost_embed)
            return True
        return False            


async def setup(bot):
    await bot.add_cog(Boost(bot))