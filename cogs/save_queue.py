import discord
from discord.ext import commands

class SaveQueue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command: Save the current queue as a playlist
    @commands.command(name="savequeue", help="Saves the current queue as a playlist.")
    async def savequeue(self, ctx, playlist_name: str):
        music_cog = self.bot.get_cog("Music")
        if music_cog and music_cog.queue:
            playlist_cog = self.bot.get_cog("Playlist")
            if playlist_cog:
                playlist_cog.save_playlist(ctx.author.id, playlist_name, music_cog.queue)
                await ctx.send(f"✅ Queue saved as playlist: `{playlist_name}`")
            else:
                await ctx.send(embed=self.create_embed("❌ Error", "Playlist cog is not loaded.", discord.Color.red()))
        else:
            await ctx.send(embed=self.create_embed("❌ Error", "The queue is empty.", discord.Color.red()))

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(SaveQueue(bot))