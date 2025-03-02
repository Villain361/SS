import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command: Display a custom help message
    @commands.command(name="h", help="Displays all available commands.")
    async def help(self, ctx):
        embed = discord.Embed(
            title="🎵 Sound Sphere Help",
            description="Here are all the available commands:",
            color=discord.Color.blue()
        )

        # Clear
        embed.add_field(
            name="Clear",
            value="`!clear` - Clears the current queue.",
            inline=False
        )

        # Controls
        embed.add_field(
            name="Controls",
            value="`!controls` - Shows music control buttons.",
            inline=False
        )

        # Help
        embed.add_field(
            name="Help",
            value="`!h` - Displays all available commands.",
            inline=False
        )

        # Leave
        embed.add_field(
            name="Leave",
            value="`!leave` - Leaves the voice channel.",
            inline=False
        )

        # Loop
        embed.add_field(
            name="Loop",
            value="`!loop <song/queue>` - Loops the current song or the entire queue.",
            inline=False
        )

        # Music
        embed.add_field(
            name="Music",
            value="`!play <query>` - Plays a song from YouTube.",
            inline=False
        )

        # NowPlaying
        embed.add_field(
            name="NowPlaying",
            value="`!nowplaying` - Shows the currently playing song.",
            inline=False
        )

        # Playlist
        embed.add_field(
            name="Playlist",
            value=(
                "`!addtoplaylist <playlist_name> <song_query>` - Adds a song to a playlist.\n"
                "`!createplaylist <playlist_name>` - Creates a new playlist.\n"
                "`!deleteplaylist <playlist_name>` - Deletes a playlist.\n"
                "`!listplaylists` - Lists all your playlists.\n"
                "`!loadplaylist <playlist_name>` - Loads a playlist into the queue."
            ),
            inline=False
        )

        # SaveQueue
        embed.add_field(
            name="SaveQueue",
            value="`!savequeue <playlist_name>` - Saves the current queue as a playlist.",
            inline=False
        )

        # Search
        embed.add_field(
            name="Search",
            value="`!search <query>` - Searches for a song on YouTube.",
            inline=False
        )

        # SkipTo
        embed.add_field(
            name="SkipTo",
            value="`!skipto <index>` - Skips to a specific song in the queue.",
            inline=False
        )

        # Footer
        embed.set_footer(text="Type `!h <command>` for more info on a command.")

        await ctx.send(embed=embed)

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(Help(bot))