import discord
from discord.ext import commands
from discord import app_commands
import logging
import typing
from cogs.music import SendMessage

logger = logging.getLogger("discord")

class pollButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        
    checkmark : bool = None
    voters = []
    msg = None
    argument = str
    downvotes = 0
    upvotes = 0
        
    embed = discord.Embed(
        title=f"💡 Votazione In Corso per: {argument}",
        description=f"# 🔺 LISTA VOTI 🔺 # \n\n",
        color=0xffc0cb
    )
        
    @discord.ui.button(label="✅ Upvote!", style=discord.ButtonStyle.success)
    async def upvote(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.checkmark = True
        if interaction.user in self.voters:
            return await interaction.response.send_message(f"Hai gia' votato.", ephemeral=True)
            
        self.voters.append(interaction.user)
        logger.info("upvote went right")
            
        logger.info("now waiting")

        self.upvotes += 1
                
        self.embed.description += f"- {interaction.user.mention}: ✅\n"

        self.embed.set_footer(text=f"✅ {self.upvotes} - ❌ {self.downvotes}")
        logger.info("edited embed desc")

        await self.msg.edit(embed=self.embed)
        logger.info("edited sent messages")
        
        await interaction.followup.send(f"<a:hellokittyexcited:1193494992967180381> Il tuo voto e' stato registrato!", ephemeral=True)
            
    @discord.ui.button(label="❌ Downvote.", style=discord.ButtonStyle.red)
    async def downvote(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.checkmark = False
        if interaction.user in self.voters:
            return await interaction.followup.send(f"Hai gia' votato.", ephemeral=True)
            
        self.voters.append(interaction.user)
        logger.info("downvote went right")

        logger.info("now waiting")

        self.downvotes += 1
        
        self.embed.description += f"- {interaction.user.mention}: ❌\n"

        self.embed.set_footer(text=f"✅ {self.upvotes} - ❌ {self.downvotes}")
        logger.info("edited embed desc")

        await self.msg.edit(embed=self.embed)
        logger.info("edited sent messages")
        
        await interaction.followup.send(f"<a:hellokittyexcited:1193494992967180381> Il tuo voto e' stato registrato!", ephemeral=True)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        self.embed.title = f'💡 Votazioni terminate per: {self.argument} '
        await self.message.edit(view=self)

class Utility(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reload(self, ctx, module: str):
        try:
            await self.bot.reload_extension(f"utils.{module}.py")
            return await ctx.send(f"<a:cinnamonwave:1193494989280378890> Reloaded `{module}.py`")
        except Exception as exc:
            logger.exception(exc)
            return await ctx.send(f"<a:cinnamonwave:1193494989280378890> Qualcosa e' andato storto: {exc}")

    @app_commands.command(description="Crea un sondaggio!")
    async def votazione(self, interaction: discord.Interaction, argomento: str):       
        view = pollButtons()
        
        embed = discord.Embed(
            title=f"Votazione per {argomento}",
            description=f"# 🔺 LISTA VOTI 🔺 # \n\n",
            color=0xffc0cb
        )
        
        m = await interaction.channel.send(embed=embed, view=view)
        view.msg = m
        view.argument = str(argomento)

        await interaction.response.send_message(f"Votazione iniziata con successo per {argomento}", ephemeral=True)
        await view.wait()

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: typing.Optional[typing.Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

async def setup(bot):
    await bot.add_cog(Utility(bot))