import discord
import logging

log = logging.getLogger("discord")

class LanguageSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="English", description="Sets the default server language for the bot to English.", emoji="🇬🇧"),
            discord.SelectOption(label="Italiano", description="Imposta la lingua del server per il bot in Italiano.", emoji="🇮🇹"),
            discord.SelectOption(label="Albanian", description="Vendos gjuhën e serverit për bot në shqip.", emoji="🇦🇱"),
            discord.SelectOption(label="Espanol", description="Establezca el idioma del servidor para el bot en español.", emoji="🇪🇸")
        ]
        
        super().__init__(placeholder="Select your language", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        
        reformats = {
            "English": "en",
            "Italian": "it",
            "Albanian": "sq",
            "Espanol": "es"
        }
        
        emoji = {
            "English": ":flag_gb:",
            "Italian": ":flag_it:",
            "Albanian": ":flag_sq:",
            "Espanol": ":flag_es:"
        }
        
        await interaction.client.pool.execute("INSERT INTO server_languages (id, lang) VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET lang = $2", interaction.guild.id, reformats[self.values[0]])       
        interaction.client.server_languages[interaction.guild.id] = reformats[self.values[0]]
        await interaction.response.defer()
        await interaction.followup.send(await interaction.client.rcm(module="Utility", command="language", event_to_call="confirmation_message", guild_id=interaction.guild.id, interaction=interaction) + f"{emoji} **{self.values[0]}**")

class LanguageView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(LanguageSelect())

class BottoneNone(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Candidatura", style=discord.ButtonStyle.green, custom_id='persistent_view:candidatura')
    async def candidatura_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_modal = StaffModal()
        await interaction.response.send_modal(staff_modal)
        
class StaffAppButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    checkmark : bool = None
    author = None
        
    @discord.ui.button(label="✅ Approva!", style=discord.ButtonStyle.success, custom_id='persistent_view:confirm')
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.checkmark = True
        self.author = interaction.user
        self.stop()
            
    @discord.ui.button(label="❌ Rifiuta.", style=discord.ButtonStyle.red, custom_id='persistent_view:reject')
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.checkmark = False
        self.author = interaction.user
        self.stop()

class StaffModal(discord.ui.Modal, title="Modulo Staff"):
    DISCORD_USERNAME = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Discord @",
        required=True,
        placeholder="Esempio: @seizou",
    )
    
    DISCORD_ID = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="ID Discord",
        required=True,
        placeholder="Inserisci il tuo Discord ID.",
    )
    
    TEMPO = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Tempo libero?",
        required=True,
        placeholder="Esempio: '2 ore ogni sera'",
    )
    
    MOTIVAZIONE = discord.ui.TextInput(
        style=discord.TextStyle.paragraph,
        label="Come mai ti stai candidando?",
        required=True,
        placeholder="Spiegaci in dettaglio il motivo della tua candidatura.",
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        
        s_tempo = self.TEMPO.value
        s_motivazione = self.MOTIVAZIONE.value
        s_username = self.DISCORD_USERNAME.value
        s_id = int(self.DISCORD_ID.value) if self.DISCORD_ID.value.isdigit() else None
        
        RUOLI = discord.ui.Select(
            options=[discord.SelectOption(label="Ticket Manager", emoji="<:vslticket:1192554270831169536>", value="Ticket Manager"), 
                     discord.SelectOption(label="Trial Helper", emoji="<:management:1192556335477297305>", value="Trial Helper")],
            placeholder="Per quale posizione ti stai candidando?",
            max_values=1
        )
        
        async def staff_app_callback(interaction: discord.Interaction):
            
            if RUOLI.values[0] == "Trial Helper":
                emoji_to_use = "<:management:1192556335477297305>"
            else:
                emoji_to_use = "<:vslticket:1192554270831169536>"
                
            await interaction.response.send_message(f"<a:hellokittyexcited:1193494992967180381> La tua `Staff Application` per il ruolo {emoji_to_use} **{RUOLI.values[0]}** e' stata inviata con successo, grazie!\n<:rolemanager:1192554243861794817> Riceverai un DM da me per aggiornamenti sulla stessa.", ephemeral=True)
            channel = interaction.guild.get_channel(1194343580467208303)
            
            embed = discord.Embed(
                description=f"# 💃 NUOVA CANDIDATURA 💃\n\n- <:blackstar:1193494590381101056> `Username Discord`: {s_username}\n"
                            f"- <:blackstar:1193494590381101056> `ID`: {s_id}\n"
                            f"- <:blackstar:1193494590381101056> `Tempo Libero`: {s_tempo}\n"
                            f"- <:blackstar:1193494590381101056> `Posizione`: {emoji_to_use} **{RUOLI.values[0]}**\n\n"
                            f"- 🔹 **`Motivazione della candidatura`**:\n{s_motivazione}",
                            color=0xffc0cb 
            )
            embed.set_author(name="💃 SLURP CREW Staff Application")
            
            view = StaffAppButtons()
            mex = await channel.send(embed=embed, view=view)
            
            memb = None
            
            if s_id:
                if isinstance(s_id, int):
                    memb = interaction.client.get_user(int(s_id))
                
            await view.wait()
            
            if view.checkmark == True:
                await mex.delete()
                try:
                    await memb.send(f"# STAFF APPLICATION #\n\n<a:hellokittyexcited:1193494992967180381> Hey hey ~! Qui per informarti che la tua candidatura staff e' stata approvata in:\n\n- **{interaction.guild.name}**\n\n"
                                           f"🔺 Se sei ancora interessato alla posizione, apri un [Ticket](https://discord.com/channels/1192455862464299058/1192457412121215097) allegando uno screen di questo messaggio per procedere!")
                    return await channel.send(f"<a:hellokittyexcited:1193494992967180381> {view.author.mention} ha approvato la candidatura di **{memb.mention if memb else s_username}** per la posizione {emoji_to_use} **{RUOLI.values[0]}**!")
                except Exception:
                    return await channel.send(f"<a:hellokittyexcited:1193494992967180381> {view.author.mention} ha approvato la candidatura di **{memb.mention if memb else s_username}** per la posizione {emoji_to_use} **{RUOLI.values[0]}**!\n"
                                              f"🔺 {memb.mention if memb else s_username} non ha i DM aperti a tutti, per tanto non posso informarlo dell'esito della candidatura, dovrete avvisarlo voi.")
            else:
                await mex.delete()
                try:
                    await memb.send(f"# STAFF APPLICATION #\n\n<a:8319hellokittyno:1193495006170861588> Hey hey ~! Qui per informarti che la tua candidatura staff e' stata rifiutata in:\n\n- **{interaction.guild.name}**\n\n")
                    return await channel.send(f"<a:8319hellokittyno:1193495006170861588> {view.author.mention} ha rifiutato la candidatura di **{memb.mention if memb else s_username}** per la posizione {emoji_to_use} **{RUOLI.values[0]}**!\n")
                except Exception:
                    return await channel.send(f"<a:8319hellokittyno:1193495006170861588> {view.author.mention} ha rifiutato la candidatura di **{memb.mention if memb else s_username}** per la posizione {emoji_to_use} **{RUOLI.values[0]}**!\n"
                                              f"🔺 {memb.mention if memb else s_username} non ha i DM aperti a tutti, per tanto non posso informarlo dell'esito della candidatura, dovrete avvisarlo voi.")
        
        RUOLI.callback = staff_app_callback
        view = discord.ui.View()
        view.add_item(RUOLI)
        
        await interaction.response.send_message(f"<a:hellokittyexcited:1193494992967180381> Ottimo! Ora dicci per quale posizione ti stai candidando!", view=view, ephemeral=True)

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
        
async def setup(bot):
    log.info("Functions Setup!")
    
async def teardown(bot):
    log.info("Functions Teardowned!")
        
        
        