from discord.ext import commands

class Integrations(commands.Cog):
    """Simulated integrations: github, reddit, twitter (demo)."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def github(self, ctx, user: str = "octocat"):
        await ctx.send(f"Fetching GitHub info for `{user}` (simulated)...\nUsername: {user}\nRepos: 42\nFollowers: 123")

    @commands.command()
    async def reddit(self, ctx, subreddit: str = "python"):
        await ctx.send(f"Fetching hot posts from r/{subreddit} (simulated)...\n1. Example Post\n2. Another Post")

    @commands.command()
    async def twitter(self, ctx, handle: str = "twitter"):
        await ctx.send(f"Latest tweet from @{handle} (simulated):\nThis is a sample tweet!")

def setup(bot):
    bot.add_cog(Integrations(bot))
