import discord
from discord.ext import commands
import random

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Helper function to create a consistent embed
    def create_embed(self, title, description, color=discord.Color.blue()):
        embed = discord.Embed(title=title, description=description, color=color)
        return embed

    # Command: Show the current queue
    @commands.command(name="queue", help="Shows the current queue.")
    async def show_queue(self, ctx):
        music_cog = self.bot.get_cog("Music")
        if music_cog and music_cog.queue:
            queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(music_cog.queue)])
            embed = self.create_embed(
                title="Current Queue",
                description=queue_list,
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("The queue is empty.")

    # Command: Shuffle the queue
    @commands.command(name="shuffle", help="Shuffles the current queue.")
    async def shuffle_queue(self, ctx):
        music_cog = self.bot.get_cog("Music")
        if music_cog and len(music_cog.queue) > 1:
            random.shuffle(music_cog.queue)
            await ctx.send("✅ Queue shuffled.")
        else:
            await ctx.send("❌ Not enough songs in the queue to shuffle.")

    # Command: Remove a specific song from the queue
    @commands.command(name="remove", help="Removes a specific song from the queue.")
    async def remove_song(self, ctx, index: int):
        music_cog = self.bot.get_cog("Music")
        if music_cog and 1 <= index <= len(music_cog.queue):
            removed_song = music_cog.queue.pop(index - 1)
            await ctx.send(f"✅ Removed: {removed_song['title']}")
        else:
            await ctx.send("❌ Invalid index. Use `!queue` to see the current queue.")

async def setup(bot):
    await bot.add_cog(Queue(bot))