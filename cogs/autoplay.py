import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
import asyncio

class Autoplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autoplay_enabled = False  # Autoplay state

    # Helper function to fetch a related song
    async def get_related_song(self, current_song):
        if not current_song:
            print("🎵 No current song found for autoplay.")  # Debug log
            return None

        search = VideosSearch(current_song['title'], limit=1)
        results = search.result()['result']
        if results:
            print(f"🎵 Found related song: {results[0]['title']}")  # Debug log
            return {
                'title': results[0]['title'],
                'url': results[0]['link'],
                'uploader': results[0]['channel']['name'],
                'duration': results[0]['duration'],
                'thumbnail': results[0]['thumbnails'][0]['url']
            }
        else:
            print("🎵 No related song found.")  # Debug log
            return None

    # Command: Toggle autoplay on/off
    @commands.command(name="autoplay", help="Toggles autoplay on/off.")
    async def autoplay(self, ctx):
        self.autoplay_enabled = not self.autoplay_enabled
        await ctx.send(f"🎵 Autoplay: {'Enabled' if self.autoplay_enabled else 'Disabled'}")

    # Listener: Handle song end event
    @commands.Cog.listener()
    async def on_song_end(self, ctx, last_song):  # Accept last_song as a parameter
        print("🎵 'song_end' event received.")  # Debug log
        if not self.autoplay_enabled:
            print("🎵 Autoplay is disabled.")  # Debug log
            return

        music_cog = self.bot.get_cog("Music")
        if music_cog and not music_cog.is_playing and not music_cog.is_paused:
            if last_song:  # Use the last_song passed from the Music cog
                print("🎵 Fetching related song...")  # Debug log
                related_song = await self.get_related_song(last_song)
                if related_song:
                    print(f"🎵 Adding related song '{related_song['title']}' to the queue.")  # Debug log
                    music_cog.queue.append(related_song)
                    await music_cog.play_next(ctx)
                else:
                    print("🎵 No related song found.")  # Debug log
            else:
                print("🎵 No last song found.")  # Debug log
                await ctx.send(embed=self.create_embed(
                    "🎵 Queue Ended",
                    "The queue is empty. Use `!play` to add more songs.",
                    discord.Color.blue()
                ), delete_after=10)  # Temporary message

    # Helper function to create a consistent embed
    def create_embed(self, title, description, color=discord.Color.blue()):
        embed = discord.Embed(title=title, description=description, color=color)
        return embed

async def setup(bot):
    await bot.add_cog(Autoplay(bot))