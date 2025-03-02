import discord
from discord.ext import commands
from discord.utils import get

class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command: Leave the voice channel
    @commands.command(name="leave", help="Leaves the voice channel.")
    async def leave(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.disconnect()
            await ctx.send(embed=self.create_embed("👋 Left", "Disconnected from the voice channel.", discord.Color.green()))
        else:
            await ctx.send(embed=self.create_embed("❌ Error", "I am not connected to a voice channel.", discord.Color.red()))

    # Helper function to create a simple embed
    def create_embed(self, title, description, color=discord.Color.blue()):
        embed = discord.Embed(title="Info", color=color)
        embed.add_field(name=title, value=description, inline=False)
        return embed

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(Leave(bot))