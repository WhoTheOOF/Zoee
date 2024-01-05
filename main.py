import discord
from discord.ext import commands
import time

selene = commands.Bot(command_prefix="s!", intents=discord.Intents.all())

class viewButtons(discord.ui.View):
    
    checkmark : bool = None
    
    @discord.ui.button(label="✅ Mi Piace!", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.checkmark = True
        time.sleep(3)
        self.stop()
        
    @discord.ui.button(label="❌ Orrendo.", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.checkmark = False
        time.sleep(3)
        self.stop()

@selene.event
async def on_ready():
    print(f'Loggato come {selene.user}!')
    
    await selene.tree.sync()

@selene.event
async def on_member_join(member: discord.Member):
    if member.guild.id == 1192455862464299058:
        embed_w = discord.Embed(description=f"# ✨ NUOVO MEMBRO ✨ # \n👋 Hey {member.mention} ~!\n\n🪐 Benvenuto nella 💃 **SLURP Crew** <3\n\n💫 Siamo un piccolo server Discord creato da alcuni amici, miriamo a creare un luogo sicuro in cui tutti possano divertirsi, così come"
                                    " avere conversazioni interessanti. :)\n\n"
                                    "# 🪐 Links Utili 🪐 #\n"
                                    "- 🖇️ [Link d'invito](https://discord.com/invite/wsBDG3ZXUf)\n"
                                    "- 👁️‍🗨️ [Pagina DISBOARD (Recensioni)](https://disboard.org/it/server/1192455862464299058)\n"
                                    "- 💭 [Chat Generale](https://discord.com/channels/1192455862464299058/1192457359239417916)\n"
                                    "- <a:slurp_icon:1190789464797216899> [Ruolo Verificato](https://discord.com/channels/1192455862464299058/1192457347352772699)\n"
                                    "- <:vslticket:1190657441956896830> [Tickets](https://discord.com/channels/1192455862464299058/1192457412121215097)\n\n"
                                    "🎊 Siamo sempre attivi! Dai un'occhio al canale [**🎉 Giveaways**](https://discord.com/channels/1192455862464299058/1192457351593214095) per vincere premi fantastici!", color=0xffc0cb)
        embed_w.set_author(name=f"⇾ Ciao {member.name} ⇽", icon_url=member.avatar.url)
        embed_w.set_image(url="https://cdn.discordapp.com/attachments/1192457322337947748/1192488696398749746/server_banner.gif?ex=65a942a4&is=6596cda4&hm=2a01caf8596219071e01cbd25356494f93e11958594c58b82644d471ef3be6c3&")
        embed_w.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}", icon_url=member.guild.icon.url)
        
        embed_g = discord.Embed(description=f"👋 Benvenuto in **{member.guild.name}**, manda il tuo primo messaggio qui!", color=0xffc0cb)
        embed_g.set_author(name=f"⇾ {member.name} ~! ⇽", icon_url=member.avatar.url)
        embed_g.set_thumbnail(url=member.avatar.url)
        embed_g.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}", icon_url=member.guild.icon.url)
        
        channel_welcome = selene.get_channel(1192457329250156654)
        channel_general = selene.get_channel(1192457359239417916)
        
        await channel_general.send(f"🎀 {member.mention} si e' appena unito al server 🎀", embed=embed_g)
        await channel_welcome.send(f"🎀 {member.mention} 🎀", embed=embed_w)
        

@selene.tree.command(description="Crea velocemente un'embed da inviare in un canale a tua scelta :)")
async def creaembed(interaction: discord.Interaction):
    def check(message):
        return message.author == interaction.user and message.channel == interaction.channel

    await interaction.response.send_message("✅ Perfetto! Ora scrivi qui in chat il titolo che vorresti per l'embed! (Se non vuoi un titolo, scrivi 'nessuno')", ephemeral=True)
    title = await selene.wait_for('message', check=check)
  
    embed = discord.Embed(color=0xffc0cb)
    embed.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}")
  
    if not title.content == "nessuno":
        embed = discord.Embed(title=title.content, color=0xffc0cb)
        embed.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}")
        await interaction.followup.send("✅ Titolo impostato! Ora manda la descrizione (Se non vuoi una descrizione, scrivi 'nessuna')", ephemeral=True)
    else:
        await interaction.followup.send("✅ Ottimo, inviero' un'embed senza titolo, ora manda la descrizione! (Se non vuoi una descrizione, scrivi 'nessuna')", ephemeral=True)      
    await title.delete()
        
    desc = await selene.wait_for('message', check=check)
    if not desc.content == "nessuna":
        embed = discord.Embed(description=desc.content, color=0xffc0cb)
        embed.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}")
        await interaction.followup.send("✅ Fantastico! Vuoi aggiungere anche il testo nella sezione autore? (Se non vuoi un testo autore, scrivi 'nessuno')", ephemeral=True)
    else:
        await interaction.followup.send("✅ Va bene, niente descrizione! Vuoi aggiungere anche il testo nella sezione autore? (Se non vuoi un testo autore, scrivi 'nessuno')", ephemeral=True)
    await desc.delete()
    
    auth = await selene.wait_for('message', check=check)
    if not auth.content == "nessuno":
        embed.set_author(name=auth.content)
        await interaction.followup.send("✅ Superbo! Un'immagine la mettiamo? (Se non vuoi un'immagine, scrivi 'no')", ephemeral=True)
    else:
        await interaction.followup.send("✅ Okok, niente autore. Un'immagine la mettiamo? Manda un link :) (Se non vuoi un'immagine, scrivi 'no')", ephemeral=True)
    await auth.delete()
        
    img = await selene.wait_for('message', check=check)
    if not img.content == "no":
        await img.delete()
        embed.set_thumbnail(url=img.content)
    
        view = viewButtons(timeout=60)
        await interaction.followup.send("✅ SUPEERRR!! Il tuo embed e' pronto, ecco una preview :)", ephemeral=True)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        
        await view.wait()
        
        if view.checkmark is None:
            return await interaction.followup.send("❓ Non hai cliccato nessun bottone.. sei vivo?", ephemeral=True)
        
        if view.checkmark == True:
            await interaction.followup.send("✅ Spettacolare! Ora dimmi in che canale devo mandarlo, menzionalo. (Assicurati che io possa mandare messaggi in quel canale)", ephemeral=True)
            channel = await selene.wait_for('message', check=check)
            if channel.content.startswith("<#") and channel.content.endswith(">"):
                await channel.delete()
                await interaction.followup.send("✅ Sei mitic*! L'embed e' stato inviato con successo!", ephemeral=True)
                int_ch = channel.content.translate({ord(i): None for i in '<#>'})
                ch = selene.get_channel(int(int_ch))
                return await ch.send(embed=embed)
            else:
                await channel.delete()
                return await interaction.followup.send(f"Canale non valido, rifai da capo.", ephemeral=True)
        else:
            return await interaction.followup.send("😥 Va bene, non mandero' l'embed, ripeti il procedimento da capo..", ephemeral=True)
    else:
        await img.delete()
        view = viewButtons(timeout=10)
        await interaction.followup.send("✅ SUPEERRR!! Il tuo embed e' pronto, ecco una preview :)", ephemeral=True)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        
        await view.wait()
        
        if view.checkmark is None:
            return await interaction.followup.send("❓ Non hai cliccato nessun bottone.. sei vivo?", ephemeral=True)
        
        if view.checkmark == True:
            await interaction.followup.send("✅ Spettacolare! Ora dimmi in che canale devo mandarlo, menzionalo. (Assicurati che io possa mandare messaggi in quel canale)", ephemeral=True)
            channel = await selene.wait_for('message', check=check)
            if channel.content.startswith("<#") and channel.content.endswith(">"):
                await channel.delete()
                await interaction.followup.send("✅ Sei mitic*! L'embed e' stato inviato con successo!", ephemeral=True)
                int_ch = channel.content.translate({ord(i): None for i in '<#>'})
                ch = selene.get_channel(int(int_ch))
                return await ch.send(embed=embed)
            else:
                await channel.delete()
                return await interaction.followup.send(f"Canale non valido, rifai da capo.", ephemeral=True)
        else:
            return await interaction.followup.send("😥 Va bene, non mandero' l'embed, ripeti il procedimento da capo..", ephemeral=True)

intents = discord.Intents.all()
intents.message_content = True

selene.run('MTE5MTg0MTY1MDQ0NDYwNzU4OA.GXinjo.tbf3bAUSj988MW0HSikn_x1xf16VbdWEZT244c')