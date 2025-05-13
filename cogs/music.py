import discord
from discord.ext import commands
import asyncio
import yt_dlp

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        "format": "bestaudio/best",
        "outtmpl": "%(id)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
    }

    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn"
    }

    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(url, download=not stream))
        if "entries" in data:
            data = data["entries"][0]
        filename = data["url"] if stream else cls.ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **cls.FFMPEG_OPTIONS), data=data)

class Music(commands.Cog):
    """Simple YouTube music commands (join, leave, play, pause, resume, stop, queue)"""

    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.is_playing = False

    async def ensure_voice(self, ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            if ctx.voice_client is None:
                await ctx.author.voice.channel.connect()
            elif ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
            return ctx.voice_client
        else:
            await ctx.send("You need to be in a voice channel!")
            return None

    @commands.command()
    async def join(self, ctx):
        """Join your voice channel."""
        vc = await self.ensure_voice(ctx)
        if vc:
            await ctx.send(f"Joined {vc.channel}")

    @commands.command()
    async def leave(self, ctx):
        """Leave the voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Left the voice channel.")
        else:
            await ctx.send("I'm not in a voice channel.")

    @commands.command()
    async def play(self, ctx, *, url):
        """Play music from a YouTube URL or search term."""
        vc = await self.ensure_voice(ctx)
        if not vc:
            return

        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            except Exception as e:
                await ctx.send(f"Error: {e}")
                return

            if vc.is_playing():
                self.queue.append((player, ctx))
                await ctx.send(f"Added to queue: {player.title}")
                return

            vc.play(player, after=lambda e: self.bot.loop.create_task(self.check_queue(ctx)))
            await ctx.send(f"Now playing: {player.title}")
            self.is_playing = True

    async def check_queue(self, ctx):
        if self.queue:
            player, orig_ctx = self.queue.pop(0)
            ctx.voice_client.play(player, after=lambda e: self.bot.loop.create_task(self.check_queue(ctx)))
            await orig_ctx.send(f"Now playing: {player.title}")
        else:
            self.is_playing = False

    @commands.command()
    async def pause(self, ctx):
        """Pause the music."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused.")

    @commands.command()
    async def resume(self, ctx):
        """Resume the music."""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed.")

    @commands.command()
    async def stop(self, ctx):
        """Stop the music and clear the queue."""
        if ctx.voice_client:
            ctx.voice_client.stop()
            self.queue.clear()
            await ctx.send("Stopped and cleared the queue.")

    @commands.command()
    async def skip(self, ctx):
        """Skip the current song."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped.")

    @commands.command()
    async def queue(self, ctx):
        """Show the current queue."""
        if self.queue:
            msg = "**Queue:**\n"
            msg += "\n".join(f"{i+1}. {p.title}" for i, (p, _) in enumerate(self.queue))
            await ctx.send(msg)
        else:
            await ctx.send("The queue is empty.")

def setup(bot):
    bot.add_cog(Music(bot))
