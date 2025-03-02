import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get
from discord.ui import Button, View
import yt_dlp as youtube_dl
import asyncio

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

# YouTube DL options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # Bind to IPv4 since IPv6 addresses cause issues sometimes
}

# FFmpeg options
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_song = None
        self.volume = 0.75  # Default volume (75%)
        self.is_playing = False
        self.is_paused = False
        self.loop_song = False  # Loop current song
        self.loop_queue = False  # Loop entire queue

    # Helper function to create a consistent embed
    def create_embed(self, title, description, color=discord.Color.blue()):
        embed = discord.Embed(title=title, description=description, color=color)
        return embed

    # Helper function to add buttons to an embed
    def add_buttons(self, view):
        pause_button = Button(emoji="⏸️", style=discord.ButtonStyle.blurple, custom_id="pause")
        resume_button = Button(emoji="▶️", style=discord.ButtonStyle.blurple, custom_id="resume")
        skip_button = Button(emoji="⏭️", style=discord.ButtonStyle.blurple, custom_id="skip")
        stop_button = Button(emoji="⏹️", style=discord.ButtonStyle.red, custom_id="stop")
        volume_button = Button(emoji="🔊", style=discord.ButtonStyle.green, custom_id="volume")

        view.add_item(pause_button)
        view.add_item(resume_button)
        view.add_item(skip_button)
        view.add_item(stop_button)
        view.add_item(volume_button)

    # Helper function to play the next song in the queue
    async def play_next(self, ctx):
        if self.loop_song and self.current_song:
            # Re-add the current song to the queue if looping is enabled
            self.queue.insert(0, self.current_song)
            print(f"🔂 Loop song enabled: Re-added '{self.current_song['title']}' to the queue.")  # Debug log
        elif self.loop_queue and self.queue:
            # Re-add the entire queue if looping is enabled
            self.queue.extend(self.queue.copy())
            print(f"🔁 Loop queue enabled: Re-added {len(self.queue)} songs to the queue.")  # Debug log

        if len(self.queue) > 0:
            self.current_song = self.queue.pop(0)
            voice = get(self.bot.voice_clients, guild=ctx.guild)

            if not voice or not voice.is_connected():
                await ctx.send(embed=self.create_embed("❌ Error", "Not connected to a voice channel.", discord.Color.red()))
                return

            # Play the song
            voice.play(FFmpegPCMAudio(self.current_song['url'], **ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = self.volume
            self.is_playing = True
            self.is_paused = False

            # Send the "Now Playing" embed with buttons
            await self.send_playing_embed(ctx)
        else:
            self.is_playing = False
            # Store the last played song before setting current_song to None
            last_song = self.current_song
            self.current_song = None
            await ctx.send(embed=self.create_embed("Queue is empty", "Use `!play` to add more songs.", discord.Color.red()))
            # Emit song end event for autoplay with the last played song
            print("🎵 Dispatching 'song_end' event.")  # Debug log
            self.bot.dispatch("song_end", ctx, last_song)  # Pass the last played song

    # Helper function to send the playing embed with buttons
    async def send_playing_embed(self, ctx):
        song = self.current_song
        embed = self.create_embed(
            title="🎶 Now Playing",
            description=f"**[{song['title']}]({song['url']})**",
            color=discord.Color.green()
        )
        embed.add_field(name="Requested By", value=ctx.author.mention, inline=False)
        embed.add_field(name="Duration", value=song.get('duration', 'Unknown'), inline=True)
        embed.add_field(name="Volume", value=f"{int(self.volume * 100)}%", inline=True)
        if song.get('thumbnail'):
            embed.set_thumbnail(url=song['thumbnail'])

        # Add buttons to the embed
        view = View()
        self.add_buttons(view)
        await ctx.send(embed=embed, view=view)

    # Command: Play a song
    @commands.command(name="play", help="Plays a song from YouTube.")
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            await ctx.send(embed=self.create_embed("❌ Error", "You are not connected to a voice channel.", discord.Color.red()))
            return

        voice_channel = ctx.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            if voice.channel != voice_channel:
                await voice.move_to(voice_channel)
        else:
            voice = await voice_channel.connect()

        async with ctx.typing():
            player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
            song = {
                'title': player.title,
                'url': player.url,
                'uploader': player.data.get('uploader'),
                'duration': player.data.get('duration'),
                'thumbnail': player.data.get('thumbnail')
            }

            self.queue.append(song)
            if not self.is_playing and not self.is_paused:
                await self.play_next(ctx)
            else:
                embed = self.create_embed(
                    title="🎵 Added to Queue",
                    description=f"**[{song['title']}]({song['url']})**",
                    color=discord.Color.green()
                )
                embed.add_field(name="Uploader", value=song['uploader'], inline=False)
                embed.add_field(name="Duration", value=song['duration'], inline=False)
                if song.get('thumbnail'):
                    embed.set_thumbnail(url=song['thumbnail'])

                await ctx.send(embed=embed)

    # Command: Pause the current song
    async def pause_command(self, interaction):
        voice = get(self.bot.voice_clients, guild=interaction.guild)
        if voice and voice.is_playing():
            voice.pause()
            self.is_paused = True
            await interaction.response.send_message("⏸️ Song paused.", ephemeral=True)  # Temporary reply
        else:
            await interaction.response.send_message("❌ No song is currently playing.", ephemeral=True)

    # Command: Resume the paused song
    async def resume_command(self, interaction):
        voice = get(self.bot.voice_clients, guild=interaction.guild)
        if voice and voice.is_paused():
            voice.resume()
            self.is_paused = False
            await interaction.response.send_message("▶️ Song resumed.", ephemeral=True)  # Temporary reply
        else:
            await interaction.response.send_message("❌ No song is currently paused.", ephemeral=True)

    # Command: Skip the current song
    async def skip_command(self, interaction):
        voice = get(self.bot.voice_clients, guild=interaction.guild)
        if voice and (voice.is_playing() or voice.is_paused()):
            voice.stop()
            await interaction.response.send_message("⏭️ Song skipped.", ephemeral=True)  # Temporary reply
            await self.play_next(await self.bot.get_context(interaction.message))
        else:
            await interaction.response.send_message("❌ No song is currently playing.", ephemeral=True)

    # Command: Stop the bot and clear the queue
    async def stop_command(self, interaction):
        voice = get(self.bot.voice_clients, guild=interaction.guild)
        if voice and (voice.is_playing() or voice.is_paused()):
            voice.stop()
            self.queue.clear()
            self.is_playing = False
            self.is_paused = False
            await interaction.response.send_message("🛑 Bot stopped and queue cleared.", ephemeral=True)  # Temporary reply
        else:
            await interaction.response.send_message("❌ No song is currently playing.", ephemeral=True)

    # Command: Set the volume
    @commands.command(name="volume", help="Adjusts the volume of the bot (0-100).")
    async def volume(self, ctx, volume: int):
        if 0 <= volume <= 100:
            self.volume = volume / 100  # Convert to a float between 0 and 1
            voice = get(self.bot.voice_clients, guild=ctx.guild)

            if voice and voice.is_playing():
                voice.source.volume = self.volume

            await ctx.send(embed=self.create_embed(
                "🔊 Volume Set",
                f"Volume set to **{volume}%**.",
                discord.Color.green()
            ))
        else:
            await ctx.send(embed=self.create_embed(
                "❌ Error",
                "Volume must be between 0 and 100.",
                discord.Color.red()
            ))

    # Button interaction handler
    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get("custom_id")

            if custom_id == "pause":
                await self.pause_command(interaction)
            elif custom_id == "resume":
                await self.resume_command(interaction)
            elif custom_id == "skip":
                await self.skip_command(interaction)
            elif custom_id == "stop":
                await self.stop_command(interaction)
            elif custom_id == "volume":
                await interaction.response.send_message("🔊 Please use the `!volume` command to set the volume.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))