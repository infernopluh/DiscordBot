from discord.ext import commands
import random

class AI(commands.Cog):
    """Simulated AI commands: chatbot, imagegen, sentiment."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def askai(self, ctx, *, question):
        responses = [
            "That's an interesting question!",
            "I'm just a bot, but I'll try my best.",
            "Let me think about that...",
            "42.",
            "Sorry, I don't know, but I'll learn!"
        ]
        await ctx.send(random.choice(responses))

    @commands.command()
    async def imagegen(self, ctx, *, prompt):
        await ctx.send(f"Here's your AI-generated image for: `{prompt}` (imagine an image here)")

    @commands.command()
    async def sentiment(self, ctx, *, text):
        sentiment = random.choice(["positive", "neutral", "negative"])
        await ctx.send(f"The sentiment of that text is: {sentiment}")

def setup(bot):
    bot.add_cog(AI(bot))
