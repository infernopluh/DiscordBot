from discord.ext import commands
import discord
import asyncio
import re
import datetime
from .badwords import BAD_WORDS

INVITE_LINK_REGEX = r"(discord\.gg/|discordapp\.com/invite/)"
LOG_CHANNEL_NAME = "mod-logs"

class Moderation(commands.Cog):
    """Comprehensive moderation with auto-moderator and logging."""

    def __init__(self, bot):
        self.bot = bot
        self.muted_role_name = "Muted"
        self.warns = {}  # In-memory; use a file/db for persistence in production

    async def send_log(self, guild, message):
        """Send a log message to the log channel, create one if missing."""
        log_channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
        if not log_channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            log_channel = await guild.create_text_channel(LOG_CHANNEL_NAME, overwrites=overwrites)
        await log_channel.send(message)

    # ========== AUTOMOD ==========
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        msg = message.content.lower()

        # Bad word filter using BAD_WORDS
        for word in BAD_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", msg):
                await message.delete()
                await message.channel.send(f"{message.author.mention} That word is not allowed here.", delete_after=5)
                await self.send_log(message.guild,
                    f":no_entry: **Filtered word** from {message.author} in {message.channel.mention}: `BLOCKED_WORD`\n> [REDACTED]")
                await self._warn(message.author, message.guild, reason="Used filtered word")
                return

        # Invite link filter (anti-ad)
        if re.search(INVITE_LINK_REGEX, msg):
            await message.delete()
            await message.channel.send(f"{message.author.mention} No invites allowed.", delete_after=5)
            await self.send_log(message.guild,
                f":no_entry: **Filtered invite link** from {message.author} in {message.channel.mention}\n> {message.content}")
            await self._warn(message.author, message.guild, reason="Posted invite link")
            return

        await self.bot.process_commands(message)

    async def _warn(self, member, guild, reason="No reason"):
        user_id = str(member.id)
        if user_id not in self.warns:
            self.warns[user_id] = []
        self.warns[user_id].append(reason)
        await self.send_log(
            guild, f":warning: Warned {member} (now has {len(self.warns[user_id])} warns): {reason}"
        )
        # Optional: auto-mute after 3 warns
        if len(self.warns[user_id]) >= 3:
            role = discord.utils.get(guild.roles, name=self.muted_role_name)
            if not role:
                role = await guild.create_role(name=self.muted_role_name)
                for channel in guild.channels:
                    await channel.set_permissions(role, speak=False, send_messages=False, add_reactions=False)
            member_obj = guild.get_member(member.id)
            if role not in member_obj.roles:
                await member_obj.add_roles(role, reason="Auto-mute after 3 warns")
                await self.send_log(guild, f":zipper_mouth: Auto-muted {member} for repeated warnings.")

    # ========== KICK ==========
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason"):
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member} for: {reason}")
        await self.send_log(ctx.guild, f":boot: {ctx.author} kicked {member} (`{reason}`)")

    # ========== BAN ==========
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason"):
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member} for: {reason}")
        await self.send_log(ctx.guild, f":hammer: {ctx.author} banned {member} (`{reason}`)")

    # ========== UNBAN ==========
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        name, discrim = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (name, discrim):
                await ctx.guild.unban(user)
                await ctx.send(f"Unbanned {user.mention}")
                await self.send_log(ctx.guild, f":unlock: {ctx.author} unbanned {user}")
                return
        await ctx.send("User not found.")

    # ========== CLEAR ==========
    @commands.command(aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Deleted {len(deleted)} messages", delete_after=5)
        await self.send_log(ctx.guild, f":wastebasket: {ctx.author} purged {len(deleted)} messages in {ctx.channel.mention}")

    # ========== MUTE / UNMUTE ==========
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason="No reason"):
        role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
        if not role:
            role = await ctx.guild.create_role(name=self.muted_role_name)
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False, add_reactions=False)
        await member.add_roles(role, reason=reason)
        await ctx.send(f"Muted {member} for: {reason}")
        await self.send_log(ctx.guild, f":zipper_mouth: {ctx.author} muted {member} (`{reason}`)")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
        if role:
            await member.remove_roles(role)
            await ctx.send(f"Unmuted {member}")
            await self.send_log(ctx.guild, f":speaking_head: {ctx.author} unmuted {member}")

    # ========== SLOWMODE ==========
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Set slowmode to {seconds} seconds.")
        await self.send_log(ctx.guild, f":snail: {ctx.author} set slowmode in {ctx.channel.mention} to {seconds}s")

    # ========== LOCK / UNLOCK CHANNEL ==========
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("Channel locked.")
        await self.send_log(ctx.guild, f":lock: {ctx.author} locked {ctx.channel.mention}")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("Channel unlocked.")
        await self.send_log(ctx.guild, f":unlock: {ctx.author} unlocked {ctx.channel.mention}")

    # ========== WARN / WARNS / CLEARWARNS ==========
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason"):
        await self._warn(member, ctx.guild, reason)
        await ctx.send(f"{member.mention} has been warned. Reason: {reason} (Total warns: {len(self.warns[str(member.id)])})")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx, member: discord.Member):
        user_id = str(member.id)
        warns = self.warns.get(user_id, [])
        if not warns:
            await ctx.send(f"{member.mention} has no warnings.")
        else:
            msg = "\n".join(f"{idx+1}. {w}" for idx, w in enumerate(warns))
            await ctx.send(f"{member.mention} has {len(warns)} warnings:\n{msg}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clearwarns(self, ctx, member: discord.Member):
        user_id = str(member.id)
        if user_id in self.warns:
            self.warns[user_id] = []
        await ctx.send(f"Cleared all warnings for {member.mention}.")
        await self.send_log(ctx.guild, f":broom: {ctx.author} cleared warns for {member}")

    # ========== NICK ==========
    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nickname=None):
        await member.edit(nick=nickname)
        await ctx.send(f"Changed nickname for {member.mention} to {nickname or member.name}")
        await self.send_log(ctx.guild, f":label: {ctx.author} changed nickname for {member} to {nickname or member.name}")

    # ========== ROLE ADD / REMOVE ==========
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, *, role: discord.Role):
        await member.add_roles(role)
        await ctx.send(f"Added {role.name} to {member.mention}")
        await self.send_log(ctx.guild, f":white_check_mark: {ctx.author} added role {role.name} to {member}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, *, role: discord.Role):
        await member.remove_roles(role)
        await ctx.send(f"Removed {role.name} from {member.mention}")
        await self.send_log(ctx.guild, f":x: {ctx.author} removed role {role.name} from {member}")

    # ========== SOFTBAN ==========
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason="No reason"):
        await member.ban(reason=reason)
        await ctx.guild.unban(member)
        await ctx.send(f"Softbanned {member} (banned and unbanned to delete messages)")
        await self.send_log(ctx.guild, f":repeat: {ctx.author} softbanned {member} (`{reason}`)")

    # ========== TIMEOUT / UNTIMEOUT ==========
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, seconds: int, *, reason="No reason"):
        try:
            until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
            await member.timeout(until, reason=reason)
            await ctx.send(f"Timed out {member} for {seconds} seconds. Reason: {reason}")
            await self.send_log(ctx.guild, f":hourglass: {ctx.author} timed out {member} for {seconds}s (`{reason}`)")
        except Exception:
            await ctx.send("Failed to timeout member. (Requires Discord's timeout permissions and API support)")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        try:
            await member.timeout(None)
            await ctx.send(f"Removed timeout for {member}.")
            await self.send_log(ctx.guild, f":hourglass_flowing_sand: {ctx.author} removed timeout for {member}")
        except Exception:
            await ctx.send("Failed to remove timeout.")

def setup(bot):
    bot.add_cog(Moderation(bot))
