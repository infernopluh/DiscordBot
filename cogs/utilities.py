from discord.ext import commands
import asyncio
import datetime

class Utility(commands.Cog):
    """Utility commands: ping, uptime, reminders, poll, user/server info."""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! Latency: {round(self.bot.latency*1000)}ms")

    @commands.command()
    async def uptime(self, ctx):
        now = datetime.datetime.utcnow()
        delta = now - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"Uptime: {hours}h {minutes}m {seconds}s")

    @commands.command()
    async def remindme(self, ctx, seconds: int, *, message: str):
        await ctx.send(f"I'll remind you in {seconds} seconds!")
        await asyncio.sleep(seconds)
        await ctx.send(f"{ctx.author.mention} Reminder: {message}")

    @commands.command()
    async def poll(self, ctx, *, question):
        msg = await ctx.send(f"📊 **Poll:** {question}\n👍 = Yes | 👎 = No")
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @commands.command()
    async def userinfo(self, ctx, member: commands.MemberConverter = None):
        member = member or ctx.author
        embed = discord.Embed(title="User Info", color=0x3498db)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Username", value=member, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title="Server Info", color=0x2ecc71)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
        embed.add_field(name="Name", value=guild.name, inline=True)
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))
