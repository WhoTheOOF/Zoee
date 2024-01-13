import discord
from discord.ext import commands
from discord import app_commands
import logging
import typing
from cogs.music import SendMessage

logger = logging.getLogger("discord")

class Utility(commands.Cog):
    
    class pollButtons(discord.ui.View):
        
        def __init__(self, argument, timeout=180):
            super().__init__(timeout=timeout)
            self.argument = argument   
                     
            self.checkmark: bool = None
            self.voters = []
            self.msg = None
            self.downvotes = 0
            self.upvotes = 0
                
            self.embed = discord.Embed(
                description=f"# 💡 Votazione in Corso # \n- `Argomento`: {self.argument}\n## 🔺 LISTA VOTI 🔺 ## \n\n",
                color=0xffc0cb
            )
        
        async def on_timeout(self):
            for child in self.children:
                child.disabled = True
                
            list_v = '\n'.join(f"{key['user_obj'].mention} {'✅' if key['final_vote'] == True else '❌'}" for key in self.voters)    
                
            closed_embed = discord.Embed(
                description=f"# 💡 Votazioni Terminate # \n- `Argomento`: {self.argument}\n## 👓 VOTI REGISTRATI 👓 ##\n{list_v}\n### 🔺 VOTI TOTALI 🔺 ### \n\n- ✅ **`{self.upvotes}`** | ❌ **`{self.downvotes}`**",
                color=0xffc0cb
            )
        
            await self.msg.edit(view=None, embed=closed_embed)
            self.downvotes = 0
            self.upvotes = 0
            self.voters.clear()
            return self.stop()
        
        @discord.ui.button(label="✅ Upvote!", style=discord.ButtonStyle.success)
        async def upvote(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            self.checkmark = True
            if interaction.user in self.voters:
                return await interaction.followup.send(f"Hai gia' votato.", ephemeral=True)
                
            data = {'user_obj': interaction.user, "final_vote": True}
                
            self.voters.append(data)

            self.upvotes += 1
                    
            self.embed.description += f"- {interaction.user.mention}: ✅\n"

            self.embed.set_footer(text=f"✅ {self.upvotes} - ❌ {self.downvotes}")

            await self.msg.edit(embed=self.embed)
            
            await interaction.followup.send(f"<a:hellokittyexcited:1193494992967180381> Il tuo voto e' stato registrato!", ephemeral=True)
                
        @discord.ui.button(label="❌ Downvote.", style=discord.ButtonStyle.red)
        async def downvote(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            self.checkmark = False
            if interaction.user in self.voters:
                return await interaction.followup.send(f"Hai gia' votato.", ephemeral=True)
                
            data = {'user_obj': interaction.user, "final_vote": False}
                
            self.voters.append(data)

            self.downvotes += 1
            
            self.embed.description += f"- {interaction.user.mention}: ❌\n"

            self.embed.set_footer(text=f"✅ {self.upvotes} - ❌ {self.downvotes}")

            await self.msg.edit(embed=self.embed)
            
            await interaction.followup.send(f"<a:hellokittyexcited:1193494992967180381> Il tuo voto e' stato registrato!", ephemeral=True)
    
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
    async def votazione(self, interaction: discord.Interaction, argomento: str, durata: int):       
        view = self.pollButtons(argomento, timeout=float(durata))
        
        embed = discord.Embed(
            description=f"# Votazione Per `{argomento}` # \n\n## 🔺 LISTA VOTI 🔺 ## \n\n",
            color=0xffc0cb
        )
        
        m = await interaction.channel.send(embed=embed, view=view)
        view.msg = m

        await interaction.response.send_message(f"✅ Il tuo sondaggio a voti per: **`{view.argument}`** e' iniziato!", ephemeral=True)
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