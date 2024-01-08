import discord
from discord.ext import commands
from datetime import datetime,timezone

class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot= bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id == 1192455862464299058:
            
            tm = datetime.now(timezone.utc)
            
            embed_w = discord.Embed(description=f"# ✨ NUOVO MEMBRO ✨ # \n👋 Hey {member.mention} ~!\n\n🪐 Benvenuto nella 💃 **SLURP Crew** <3\n\n💫 Siamo un piccolo server Discord creato da alcuni amici, miriamo a creare un luogo sicuro in cui tutti possano divertirsi, così come"
                                        " avere conversazioni interessanti. :)\n\n"
                                        "# 🪐 Links Utili 🪐 #\n"
                                        "- 🖇️ [Link d'invito](https://discord.com/invite/wsBDG3ZXUf)\n"
                                        "- 👁️‍🗨️ [Pagina DISBOARD (Recensioni)](https://disboard.org/it/server/1192455862464299058)\n"
                                        "- 💭 [Chat Generale](https://discord.com/channels/1192455862464299058/1192457359239417916)\n"
                                        "- <a:1963blackbutterfly:1193494553160843316> [Ruolo Verificato](https://discord.com/channels/1192455862464299058/1192457347352772699)\n"
                                        "- <:vslticket:1192554270831169536> [Tickets](https://discord.com/channels/1192455862464299058/1192457412121215097)\n\n"
                                        "🎊 Siamo sempre attivi! Dai un'occhio al canale [**🎉 Giveaways**](https://discord.com/channels/1192455862464299058/1192457351593214095) per vincere premi fantastici!", color=0xffc0cb)
            embed_w.set_author(name=f"⇾ Ciao {member.name} ⇽", icon_url=member.avatar.url if member.avatar.url != None else member.guild.icon.url)
            embed_w.set_image(url="https://cdn.discordapp.com/attachments/1192457322337947748/1192488696398749746/server_banner.gif?ex=65a942a4&is=6596cda4&hm=2a01caf8596219071e01cbd25356494f93e11958594c58b82644d471ef3be6c3&")
            embed_w.set_footer(text=f"Oggi alle {tm.strftime('%H:%M')}", icon_url=member.guild.icon.url)
            
            embed_g = discord.Embed(description=f"👋 Benvenuto in **{member.guild.name}**, manda il tuo primo messaggio qui!", color=0xffc0cb)
            embed_g.set_author(name=f"⇾ {member.name} ~! ⇽", icon_url=member.avatar.url if member.avatar.url != None else member.guild.icon.url)
            embed_g.set_thumbnail(url=member.avatar.url if member.avatar.url != None else member.guild.icon.url)
            embed_g.set_footer(text=f"Oggi alle {tm.strftime('%H:%M')}", icon_url=member.guild.icon.url)
            
            channel_welcome = self.bot.get_channel(1192457329250156654)
            channel_general = self.bot.get_channel(1192457359239417916)
            
            await channel_general.send(f"🎀 {member.mention} si e' appena unito al server 🎀", embed=embed_g)
            await channel_welcome.send(f"🎀 {member.mention} 🎀", embed=embed_w)
            
async def setup(bot):
    await bot.add_cog(Welcome(bot))