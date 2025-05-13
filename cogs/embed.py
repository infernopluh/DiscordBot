from discord.ext import commands
import discord

class EmbedCog(commands.Cog):
    """Lets users send their message as an embed."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def embed(self, ctx, *, message: str = None):
        if not message:
            await ctx.send("Please provide a message to embed, e.g. `!embed Your text here`.")
            return

        embed = discord.Embed(
            description=message,
            color=discord.Color.blurple()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass  # Ignore if bot can't delete message

def setup(bot):
    bot.add_cog(EmbedCog(bot))
