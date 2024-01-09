import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import datetime
import typing
import logging
import os

log = logging.getLogger(__name__)
discord.utils.setup_logging(level=logging.INFO)

class StaffModal(discord.ui.Modal, title="Modulo Staff"):
    DISCORD_USERNAME = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Discord @",
        required=True,
        placeholder="Esempio: @seizou",
    )
    
    EMAIL = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Indirizzo Email",
        required=True,
        placeholder="Inserisci il tuo indirizzo email",
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        
        RUOLI = discord.ui.Select(
            options=[discord.SelectOption(label="ruolo 1", value="test1"), discord.SelectOption(label="ruolo 2", value="test2"), discord.SelectOption(label="ruolo 3", value="test3")]
        )
        
        view = discord.ui.View()
        view.add_item(RUOLI)
        
        return await interaction.response.send_message(f"{StaffModal.DISCORD_USERNAME}, {StaffModal.EMAIL}, {StaffModal.RUOLO}", view=view, ephemeral=True)

class EmbedModal(discord.ui.Modal, title="Clicca qui!"): 
    EMBED_TITLE = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="NUOVO TITOLO EMBED",
        required=False,
        placeholder="Non inserire nulla per non modificarlo.",
    )
    
    EMBED_DESC = discord.ui.TextInput(
        style=discord.TextStyle.paragraph,
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

class SendMessage():

    async def as_interaction(interaction: discord.Interaction, content: str, eph: True):
        try:
            await interaction.response.defer()
            await interaction.followup.send(content=content, ephemeral=eph)
        except Exception as exception:
            return log.error(f"✕ Errore in as_interaction (functions.py): {exception}")
        
async def setup(bot):
    log.info("[INFO] Functions Loaded.")

async def teardown(bot):
    print('[INFO] Functions Unloaded.')
        
        
        