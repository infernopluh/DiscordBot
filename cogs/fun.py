from discord.ext import commands
import random

class Fun(commands.Cog):
    """Fun & games commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, dice: str = "1d6"):
        """Roll a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.lower().split("d"))
        except Exception:
            await ctx.send("Format must be NdN (2d6, 1d20, etc)")
            return
        result = [str(random.randint(1, limit)) for _ in range(rolls)]
        await ctx.send(", ".join(result))

    @commands.command()
    async def joke(self, ctx):
        jokes = [
            "Why did the chicken join a band? Because it had the drumsticks!",
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call fake spaghetti? An impasta!",
            "I told my computer I needed a break, and it said 'No problem, I’ll go to sleep.'"
        ]
        await ctx.send(random.choice(jokes))

    @commands.command()
    async def meme(self, ctx):
        memes = [
            "https://i.imgflip.com/30b1gx.jpg",
            "https://i.imgflip.com/1bij.jpg",
            "https://i.redd.it/3rze4b4f1xi51.jpg"
        ]
        await ctx.send(random.choice(memes))

    @commands.command()
    async def coinflip(self, ctx):
        await ctx.send(random.choice(["Heads", "Tails"]))

    @commands.command()
    async def eightball(self, ctx, *, question):
        responses = [
            "Yes.", "No.", "Maybe.", "Definitely!", "I don't think so.",
            "Absolutely.", "Ask again later.", "I have no idea!"
        ]
        await ctx.send(f"🎱 {random.choice(responses)}")

    @commands.command()
    async def rate(self, ctx, *, thing):
        await ctx.send(f"I rate {thing} a {random.randint(1, 10)}/10!")

def setup(bot):
    bot.add_cog(Fun(bot))
