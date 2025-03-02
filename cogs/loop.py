import discord
from discord.ext import commands

class Loop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="loop", help="Loops the current song or the entire queue.")
    async def loop(self, ctx, mode: str = None):
        music_cog = self.bot.get_cog("Music")
        if not music_cog:
            await ctx.send("❌ Music cog is not loaded.")
            return

        if mode is None:
            await ctx.send("❌ Please specify a loop mode: `!loop song` or `!loop queue`.")
            return

        mode = mode.lower()  # Convert to lowercase for case-insensitive comparison

        if mode == "song":
            music_cog.loop_song = not music_cog.loop_song
            music_cog.loop_queue = False
            await ctx.send(f"🔂 Loop song: {'Enabled' if music_cog.loop_song else 'Disabled'}")
            print(f"Loop song: {music_cog.loop_song}")  # Debug log
        elif mode == "queue":
            music_cog.loop_queue = not music_cog.loop_queue
            music_cog.loop_song = False
            await ctx.send(f"🔁 Loop queue: {'Enabled' if music_cog.loop_queue else 'Disabled'}")
            print(f"Loop queue: {music_cog.loop_queue}")  # Debug log
        else:
            await ctx.send("❌ Invalid loop mode. Use `!loop song` or `!loop queue`.")

async def setup(bot):
    await bot.add_cog(Loop(bot))