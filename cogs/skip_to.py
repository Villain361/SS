import discord
from discord.ext import commands

class SkipTo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command: Skip to a specific song in the queue
    @commands.command(name="skipto", help="Skips to a specific song in the queue.")
    async def skipto(self, ctx, index: int):
        music_cog = self.bot.get_cog("Music")
        if music_cog and 1 <= index <= len(music_cog.queue):
            music_cog.queue = music_cog.queue[index - 1:]
            await music_cog.skip(ctx)
        else:
            await ctx.send(embed=self.create_embed("❌ Error", "Invalid index. Use `!queue` to see the current queue.", discord.Color.red()))

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(SkipTo(bot))