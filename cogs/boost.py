import discord
from discord.ext import commands
from datetime import datetime,timezone

class Boost(commands.Cog):

    def __init__(self, bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_message(self, message):
        
        if "MessageType.premium_guild" in str(message.type):
            tm = datetime.now(timezone.utc)
            
            channel = self.bot.get_channel(1192457359239417916)
            db = discord.utils.get(message.guild.roles, id=1192951322350190783)
            
            double_boost_embed = discord.Embed(
                description=f"# 🦋 NUOVO BOOST 🦋 #\n\n<:discordboost:1192556344159522986> Grazie mille per il secondo boost {message.author.mention} <3\n<:3503rolemanager:1192554243861794817> Hai ricevuto il ruolo {db.mention} ~!",
                color = 0xffc0cb
            )
            double_boost_embed.set_author(name=f"⇾ 💃 SLURP CREW Annuncio Double Boost ⇽", icon_url=message.guild.icon.url)
            double_boost_embed.set_footer(text=f"Oggi alle {tm.strftime('%H:%M')}", icon_url=message.guild.icon.url)
            
            m = message.guild.get_member(message.author.id)
            r = message.guild.get_role(1192555588115247164)
            if r in m.roles:
                await message.author.add_roles(db)
                return await channel.send(embed=double_boost_embed)
            
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.premium_since is not None and after.premium_since is None:
            db = discord.utils.get(after.guild.roles, id=1192951322350190783)
            await self.bot.remove_roles(after, db)
        elif before.premium_since is None and after.premium_since is not None:
            tm = datetime.now(timezone.utc)
            channel = after.guild.get_channel(1192457359239417916)
            sb = discord.utils.get(after.guild.roles, id=1192555588115247164)
            server_boost_embed = discord.Embed(
                description=f"# 🦋 NUOVO BOOST 🦋 #\n\n<:discordboost:1192556344159522986> Grazie mille per il boost {after.mention} <3\n<:3503rolemanager:1192554243861794817> Hai ricevuto il ruolo {sb.mention} ~!",
                color = 0xffc0cb
            )
            server_boost_embed.set_author(name=f"⇾ 💃 SLURP CREW Annuncio Boost ⇽", icon_url=after.guild.icon.url)
            server_boost_embed.set_footer(text=f"Oggi alle {tm.strftime('%H:%M')}", icon_url=after.guild.icon.url)            
            
            return await channel.send(embed=server_boost_embed)

async def setup(bot):
    await bot.add_cog(Boost(bot))