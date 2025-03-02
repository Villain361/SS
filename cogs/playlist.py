import discord
from discord.ext import commands
import json
import os

# Ensure the playlists directory exists
if not os.path.exists("data/playlists"):
    os.makedirs("data/playlists")

class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Helper function to load a playlist
    def load_playlist(self, user_id, playlist_name):
        file_path = f"data/playlists/{user_id}_{playlist_name}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
        return None

    # Helper function to save a playlist
    def save_playlist(self, user_id, playlist_name, songs):
        file_path = f"data/playlists/{user_id}_{playlist_name}.json"
        with open(file_path, "w") as file:
            json.dump(songs, file)

    # Helper function to delete a playlist
    def delete_playlist(self, user_id, playlist_name):
        file_path = f"data/playlists/{user_id}_{playlist_name}.json"
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    # Command: Create a playlist
    @commands.command(name="createplaylist", help="Creates a new playlist.")
    async def create_playlist(self, ctx, playlist_name: str):
        user_id = ctx.author.id
        file_path = f"data/playlists/{user_id}_{playlist_name}.json"
        if os.path.exists(file_path):
            await ctx.send(f"A playlist with the name '{playlist_name}' already exists.")
        else:
            self.save_playlist(user_id, playlist_name, [])
            await ctx.send(f"Playlist '{playlist_name}' created.")

    # Command: Add a song to a playlist
    @commands.command(name="addtoplaylist", help="Adds a song to a playlist.")
    async def add_to_playlist(self, ctx, playlist_name: str, *, song_query: str):
        user_id = ctx.author.id
        playlist = self.load_playlist(user_id, playlist_name)
        if playlist is None:
            await ctx.send(f"Playlist '{playlist_name}' does not exist.")
            return

        # Search for the song (using the same logic as in music.py)
        from youtubesearchpython import VideosSearch
        search = VideosSearch(song_query, limit=1)
        result = search.result()['result'][0]
        song = {
            'title': result['title'],
            'url': result['link'],
            'uploader': result['channel']['name'],
            'duration': result['duration'],
            'thumbnail': result['thumbnails'][0]['url']
        }

        playlist.append(song)
        self.save_playlist(user_id, playlist_name, playlist)
        await ctx.send(f"Added '{song['title']}' to playlist '{playlist_name}'.")

    # Command: Load a playlist into the queue
    @commands.command(name="loadplaylist", help="Loads a playlist into the queue.")
    async def load_playlist(self, ctx, playlist_name: str):
        user_id = ctx.author.id
        playlist = self.load_playlist(user_id, playlist_name)
        if playlist is None:
            await ctx.send(f"Playlist '{playlist_name}' does not exist.")
            return

        music_cog = self.bot.get_cog("Music")
        if music_cog:
            for song in playlist:
                music_cog.queue.append(song)
            await ctx.send(f"Playlist '{playlist_name}' loaded into the queue.")
            if not music_cog.is_playing and not music_cog.is_paused:
                await music_cog.play_next(ctx)
        else:
            await ctx.send("Music cog is not loaded.")

    # Command: Delete a playlist
    @commands.command(name="deleteplaylist", help="Deletes a playlist.")
    async def delete_playlist(self, ctx, playlist_name: str):
        user_id = ctx.author.id
        if self.delete_playlist(user_id, playlist_name):
            await ctx.send(f"Playlist '{playlist_name}' deleted.")
        else:
            await ctx.send(f"Playlist '{playlist_name}' does not exist.")

    # Command: List all playlists
    @commands.command(name="listplaylists", help="Lists all your playlists.")
    async def list_playlists(self, ctx):
        user_id = ctx.author.id
        playlists = []
        for filename in os.listdir("data/playlists"):
            if filename.startswith(f"{user_id}_"):
                playlists.append(filename[len(f"{user_id}_"):-5])  # Remove user ID and .json

        if playlists:
            await ctx.send(f"Your playlists: {', '.join(playlists)}")
        else:
            await ctx.send("You have no playlists.")

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(Playlist(bot))