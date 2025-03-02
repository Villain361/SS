import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
import asyncio

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Helper function to create a consistent embed
    def create_embed(self, title, description, color=discord.Color.blue()):
        embed = discord.Embed(title=title, description=description, color=color)
        return embed

    # Command: Search for a song on YouTube
    @commands.command(name="search", help="Searches for a song on YouTube.")
    async def search_song(self, ctx, *, query: str):
        search = VideosSearch(query, limit=5)  # Limit to 5 results
        results = search.result()['result']

        if not results:
            await ctx.send(embed=self.create_embed("❌ Error", "No results found.", discord.Color.red()))
            return

        # Create an embed for search results
        embed = discord.Embed(
            title="🎵 Search Results",
            description="Here are the top 5 results:",
            color=discord.Color.blue()
        )
        for i, result in enumerate(results):
            title = result['title']
            duration = result['duration']
            uploader = result['channel']['name']
            embed.add_field(
                name=f"{i+1}. {title}",
                value=f"Duration: {duration} | Uploader: {uploader}",
                inline=False
            )
        embed.set_footer(text="Type the number of the song you want to play.")
        await ctx.send(embed=embed)

        # Wait for the user to choose a song
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            choice = int(msg.content)
            if 1 <= choice <= len(results):
                selected_song = results[choice - 1]
                song = {
                    'title': selected_song['title'],
                    'url': selected_song['link'],
                    'uploader': selected_song['channel']['name'],
                    'duration': selected_song['duration'],
                    'thumbnail': selected_song['thumbnails'][0]['url']
                }

                # Add the selected song to the queue
                music_cog = self.bot.get_cog("Music")
                if music_cog:
                    music_cog.queue.append(song)
                    await ctx.send(embed=self.create_embed(
                        "✅ Song Added to Queue",
                        f"**[{song['title']}]({song['url']})**",
                        discord.Color.green()
                    ))

                    # Start playing if no song is currently playing
                    if not music_cog.is_playing and not music_cog.is_paused:
                        await music_cog.play_next(ctx)
                else:
                    await ctx.send(embed=self.create_embed(
                        "❌ Error",
                        "Music cog is not loaded.",
                        discord.Color.red()
                    ))
            else:
                await ctx.send(embed=self.create_embed(
                    "❌ Error",
                    "Invalid choice.",
                    discord.Color.red()
                ))
        except asyncio.TimeoutError:
            await ctx.send(embed=self.create_embed(
                "❌ Error",
                "You took too long to choose a song.",
                discord.Color.red()
            ))

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(Search(bot))