import discord
from discord.ext import commands
from discord.ui import Button, View

class Controls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="controls", help="Shows music control buttons.")
    async def controls(self, ctx):
        view = View()

        # Pause/Resume button
        pause_resume_button = Button(label="⏯️ Pause/Resume", style=discord.ButtonStyle.blurple)
        pause_resume_button.callback = self.pause_resume_callback
        view.add_item(pause_resume_button)

        # Skip button
        skip_button = Button(label="⏭️ Skip", style=discord.ButtonStyle.blurple)
        skip_button.callback = self.skip_callback
        view.add_item(skip_button)

        # Stop button
        stop_button = Button(label="⏹️ Stop", style=discord.ButtonStyle.red)
        stop_button.callback = self.stop_callback
        view.add_item(stop_button)

        await ctx.send("Control the music:", view=view)

    async def pause_resume_callback(self, interaction):
        music_cog = self.bot.get_cog("Music")
        if music_cog:
            if music_cog.is_paused:
                await music_cog.resume(interaction)
            else:
                await music_cog.pause(interaction)
        await interaction.response.defer()

    async def skip_callback(self, interaction):
        music_cog = self.bot.get_cog("Music")
        if music_cog:
            await music_cog.skip(interaction)
        await interaction.response.defer()

    async def stop_callback(self, interaction):
        music_cog = self.bot.get_cog("Music")
        if music_cog:
            await music_cog.stop(interaction)
        await interaction.response.defer()

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(Controls(bot))