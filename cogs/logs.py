from discord.ext import commands
import discord
import datetime

LOG_CHANNEL_NAME = "mod-logs"

class ModLogs(commands.Cog):
    """Logs moderation, member, and audit log events to the #mod-logs channel."""

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

    # ========== AUDIT LOG EVENTS ==========
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        log_channel = await self.get_log_channel(after.guild)
        # Nickname changes
        if before.nick != after.nick:
            embed = discord.Embed(
                title="Nickname Changed",
                description=f"{after.mention} changed nickname\n**Before:** {before.nick}\n**After:** {after.nick}",
                color=0xff9900,
                timestamp=datetime.datetime.utcnow()
            )
            await log_channel.send(embed=embed)
        # Role changes
        if set(before.roles) != set(after.roles):
            before_roles = set(before.roles)
            after_roles = set(after.roles)
            added_roles = [role for role in after_roles - before_roles]
            removed_roles = [role for role in before_roles - after_roles]
            changes = ""
            if added_roles:
                changes += f"**Added Roles:** {', '.join(role.mention for role in added_roles)}\n"
            if removed_roles:
                changes += f"**Removed Roles:** {', '.join(role.mention for role in removed_roles)}\n"
            if changes:
                embed = discord.Embed(
                    title="Roles Updated",
                    description=f"{after.mention}\n{changes}",
                    color=0xaaaa00,
                    timestamp=datetime.datetime.utcnow()
                )
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        log_channel = await self.get_log_channel(after)
        changes = []
        if before.name != after.name:
            changes.append(f"**Server renamed:** `{before.name}` → `{after.name}`")
        if before.icon != after.icon:
            changes.append(f"**Server icon changed**")
        if changes:
            embed = discord.Embed(
                title="Server Updated",
                description="\n".join(changes),
                color=0x00ffcc,
                timestamp=datetime.datetime.utcnow()
            )
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        log_channel = await self.get_log_channel(role.guild)
        embed = discord.Embed(
            title="Role Created",
            description=f"Role {role.mention} was created.",
            color=0xdddd00,
            timestamp=datetime.datetime.utcnow()
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        log_channel = await self.get_log_channel(role.guild)
        embed = discord.Embed(
            title="Role Deleted",
            description=f"Role `{role.name}` was deleted.",
            color=0xff8800,
            timestamp=datetime.datetime.utcnow()
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        log_channel = await self.get_log_channel(after.guild)
        changes = []
        if before.name != after.name:
            changes.append(f"**Role renamed:** `{before.name}` → `{after.name}`")
        if before.color != after.color:
            changes.append(f"**Role color changed**")
        if before.permissions != after.permissions:
            changes.append(f"**Role permissions changed**")
        if changes:
            embed = discord.Embed(
                title="Role Updated",
                description="\n".join(changes),
                color=0xccff00,
                timestamp=datetime.datetime.utcnow()
            )
            await log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(ModLogs(bot))
