from discord.ext import commands
import discord
import datetime

LOG_CHANNEL_NAME = "mod-logs"

class ModLogs(commands.Cog):
    """Logs moderation & member events to the #mod-logs channel."""

    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild):
        log_channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
        if log_channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            log_channel = await guild.create_text_channel(LOG_CHANNEL_NAME, overwrites=overwrites)
        return log_channel

    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = await self.get_log_channel(member.guild)
        embed = discord.Embed(
            title="Member Joined",
            description=f"{member.mention} ({member}) joined.",
            color=0x00ff00,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_channel = await self.get_log_channel(member.guild)
        embed = discord.Embed(
            title="Member Left",
            description=f"{member.mention} ({member}) left.",
            color=0xff0000,
            timestamp=datetime.datetime.utcnow()
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        log_channel = await self.get_log_channel(guild)
        embed = discord.Embed(
            title="Member Banned",
            description=f"{user.mention if hasattr(user, 'mention') else user} was banned.",
            color=0x990000,
            timestamp=datetime.datetime.utcnow()
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        log_channel = await self.get_log_channel(guild)
        embed = discord.Embed(
            title="Member Unbanned",
            description=f"{user.mention if hasattr(user, 'mention') else user} was unbanned.",
            color=0x00aaaa,
            timestamp=datetime.datetime.utcnow()
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return
        log_channel = await self.get_log_channel(message.guild)
        embed = discord.Embed(
            title="Message Deleted",
            description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Content:**\n{message.content}",
            color=0xffbb00,
            timestamp=datetime.datetime.utcnow()
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild:
            return
        if before.content == after.content:
            return
        log_channel = await self.get_log_channel(before.guild)
        embed = discord.Embed(
            title="Message Edited",
            description=(
                f"**Author:** {before.author.mention}\n"
                f"**Channel:** {before.channel.mention}\n"
                f"**Before:** {before.content}\n"
                f"**After:** {after.content}"
            ),
            color=0x00bfff,
            timestamp=datetime.datetime.utcnow()
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if before.name != after.name:
            log_channel = await self.get_log_channel(after.guild)
            embed = discord.Embed(
                title="Channel Renamed",
                description=f"{before.mention} renamed to {after.mention}",
                color=0xaaaaaa,
                timestamp=datetime.datetime.utcnow()
            )
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        log_channel = await self.get_log_channel(channel.guild)
        embed = discord.Embed(
            title="Channel Created",
            description=f"{channel.mention} was created.",
            color=0x55ff55,
            timestamp=datetime.datetime.utcnow()
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel = await self.get_log_channel(channel.guild)
        embed = discord.Embed(
            title="Channel Deleted",
            description=f"{channel.name} was deleted.",
            color=0xff5555,
            timestamp=datetime.datetime.utcnow()
        )
        await log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(ModLogs(bot))
