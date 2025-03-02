import discord
from discord.ext import commands

class NowPlaying(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command: Show the currently playing song
    @commands.command(name="nowplaying", help="Shows the currently playing song.")
    async def nowplaying(self, ctx):
        music_cog = self.bot.get_cog("Music")
        if music_cog and music_cog.current_song:
            await music_cog.send_playing_embed(ctx)
        else:
            await ctx.send(embed=self.create_embed("❌ Error", "No song is currently playing.", discord.Color.red()))

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(NowPlaying(bot))