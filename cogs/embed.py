import discord
from discord.ext import commands
from discord import app_commands
import time
from discord import NotFound

class EmbedModal(discord.ui.Modal, title="Clicca qui!"): 
    EMBED_TITLE = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="NUOVO TITOLO EMBED",
        required=False,
        placeholder="Non inserire nulla per non modificarlo.",
    )
    
    EMBED_DESC = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="NUOVA DESCRIZIONE EMBED",
        required=False,
        placeholder="Non inserire nulla per non modificarla.",
    )
    
    EMBED_IMG = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="LINK NUOVA IMMAGINE EMBED",
        required=False,
        placeholder="Non inserire nulla per non modificarla.",
    )
    
    EMBED_AUTH = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="NUOVO TESTO AUTHOR EMBED",
        required=False,
        placeholder="Non inserire nulla per non modificarlo.",
    )

    async def on_submit(self, interaction: discord.Interaction):
        
        msg = None
        etitle = self.EMBED_TITLE if self.EMBED_TITLE != None else None
        edesc = self.EMBED_DESC if self.EMBED_DESC != None else None
        eimg = self.EMBED_IMG if self.EMBED_IMG != None else None
        eauthor = self.EMBED_AUTH if self.EMBED_AUTH != None else None
        
        edited_embed = discord.Embed(color = 0xffc0cb)
        
        if etitle:
            edited_embed.title = etitle.value
        if edesc:
            edited_embed.description = edesc.value
        if eimg:
            edited_embed.set_thumbnail(url=eimg if eimg.value.startswith("https://") and eimg.value.endswith(".png") else None)
        if eauthor:
            edited_embed.set_author(name=eauthor.value)
        
        cha = interaction.client.get_channel(int(self.ch))
        msg = await cha.fetch_message(int(self.id))

        if msg != None:
            await msg.edit(embed=edited_embed)
            return await interaction.response.send_message(f"✅ Modificato con successo! **`(ID: {int(self.id)})`**", ephemeral=True)
        elif msg == None:
            return await interaction.response.send_message(f"🔺 Embed non trovato, prova di nuovo. **`(ID: {int(self.id)})`**", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"🔺 Qualcosa e' andato storto.. riprova. **`(ID: {int(self.id)})`**\n{error}", ephemeral=True)

class viewButtons(discord.ui.View):
        
    checkmark : bool = None
        
    @discord.ui.button(label="✅ Mi Piace!", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.checkmark = True
        self.stop()
            
    @discord.ui.button(label="❌ Orrendo.", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.checkmark = False
        self.stop()

def is_staff(interaction: discord.Interaction):
    allowed_members_ids = ["144126010642792449", "695661153388331118"]
    if str(interaction.user.id) in allowed_members_ids:
        return True
    return False

class Embed(commands.Cog):

    def __init__(self, bot):
        self.bot= bot
    
    class EmbedGroup(app_commands.Group):
        
        @app_commands.command(description="Crea velocemente un'embed da inviare in un canale a tua scelta (sempre se funziona) :)")
        @app_commands.check(is_staff)
        async def create(self, interaction: discord.Interaction):
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel

            await interaction.response.send_message("✅ Perfetto! Ora scrivi qui in chat il titolo che vorresti per l'embed! (Se non vuoi un titolo, scrivi 'nessuno')", ephemeral=True)
            title = await interaction.client.wait_for('message', check=check)
        
            embed = discord.Embed(color=0xffc0cb)
            embed.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}")
        
            if not title.content == "nessuno":
                embed = discord.Embed(title=title.content, color=0xffc0cb)
                embed.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}")
                await interaction.followup.send("✅ Titolo impostato! Ora manda la descrizione (Se non vuoi una descrizione, scrivi 'nessuna')", ephemeral=True)
            else:
                await interaction.followup.send("✅ Ottimo, inviero' un'embed senza titolo, ora manda la descrizione! (Se non vuoi una descrizione, scrivi 'nessuna')", ephemeral=True)      
            await title.delete()
                
            desc = await interaction.client.wait_for('message', check=check)
            if not desc.content == "nessuna":
                embed = discord.Embed(description=desc.content, color=0xffc0cb)
                embed.set_footer(text=f"Oggi alle {time.strftime('%H:%M')}")
                await interaction.followup.send("✅ Fantastico! Vuoi aggiungere anche il testo nella sezione autore? (Se non vuoi un testo autore, scrivi 'nessuno')", ephemeral=True)
            else:
                await interaction.followup.send("✅ Va bene, niente descrizione! Vuoi aggiungere anche il testo nella sezione autore? (Se non vuoi un testo autore, scrivi 'nessuno')", ephemeral=True)
            await desc.delete()
            
            auth = await interaction.client.wait_for('message', check=check)
            if not auth.content == "nessuno":
                embed.set_author(name=auth.content)
                await interaction.followup.send("✅ Superbo! Un'immagine la mettiamo? (Se non vuoi un'immagine, scrivi 'no')", ephemeral=True)
            else:
                await interaction.followup.send("✅ Okok, niente autore. Un'immagine la mettiamo? Manda un link :) (Se non vuoi un'immagine, scrivi 'no')", ephemeral=True)
            await auth.delete()
                
            img = await interaction.client.wait_for('message', check=check)
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
                    channel = await interaction.client.wait_for('message', check=check)
                    if channel.content.startswith("<#") and channel.content.endswith(">"):
                        await channel.delete()
                        await interaction.followup.send("✅ Sei mitic*! L'embed e' stato inviato con successo!", ephemeral=True)
                        int_ch = channel.content.translate({ord(i): None for i in '<#>'})
                        ch = interaction.client.get_channel(int(int_ch))
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
                    channel = await interaction.client.wait_for('message', check=check)
                    if channel.content.startswith("<#") and channel.content.endswith(">"):
                        await channel.delete()
                        await interaction.followup.send("✅ Sei mitic*! L'embed e' stato inviato con successo!", ephemeral=True)
                        int_ch = channel.content.translate({ord(i): None for i in '<#>'})
                        ch = interaction.client.get_channel(int(int_ch))
                        return await ch.send(embed=embed)
                    else:
                        await channel.delete()
                        return await interaction.followup.send(f"Canale non valido, rifai da capo.", ephemeral=True)
                else:
                    return await interaction.followup.send("😥 Va bene, non mandero' l'embed, ripeti il procedimento da capo..", ephemeral=True)

        @app_commands.command(description="Modifica un'embed gia' inviato nel server!")
        @app_commands.check(is_staff)
        async def modifica(self, interaction: discord.Interaction, id_canale: str, embed_id: str):
            e_modal = EmbedModal()
            e_modal.id = embed_id
            e_modal.ch = id_canale
            await interaction.response.send_modal(e_modal)   
        
async def setup(bot: commands.Bot):
    bot.tree.add_command(Embed.EmbedGroup(name="embed"))
    await bot.add_cog(Embed(bot))