from discord.ext import commands
import discord

class Moderation(commands.Cog):
    """Moderation commands like kick, ban, mute, clear, slowmode, etc."""

    def __init__(self, bot):
        self.bot = bot
        self.muted_role_name = "Muted"

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason"):
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member} for: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason"):
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member} for: {reason}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Deleted {len(deleted)} messages", delete_after=5)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason="No reason"):
        role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
        if not role:
            role = await ctx.guild.create_role(name=self.muted_role_name)
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False)
        await member.add_roles(role, reason=reason)
        await ctx.send(f"Muted {member} for: {reason}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
        if role:
            await member.remove_roles(role)
            await ctx.send(f"Unmuted {member}")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Set slowmode to {seconds} seconds.")

def setup(bot):
    bot.add_cog(Moderation(bot))
