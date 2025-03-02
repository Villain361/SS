import discord
from discord.ext import commands
import lyricsgenius

genius = lyricsgenius.Genius("YOUR_GENIUS_API_KEY")

class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command: Fetch lyrics for the currently playing song
    @commands.command(name="lyrics", help="Fetches lyrics for the currently playing song.")
    async def lyrics(self, ctx):
        music_cog = self.bot.get_cog("Music")
        if music_cog and music_cog.current_song:
            song = genius.search_song(music_cog.current_song['title'])
            if song:
                await ctx.send(f"🎵 Lyrics for **{song.title}**:\n{song.lyrics}")
            else:
                await ctx.send(embed=self.create_embed("❌ Error", "No lyrics found for this song.", discord.Color.red()))
        else:
            await ctx.send(embed=self.create_embed("❌ Error", "No song is currently playing.", discord.Color.red()))

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(Lyrics(bot))