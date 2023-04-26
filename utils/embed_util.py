import discord
import wavelink
import datetime
from config import PREVIOUS_TRACKS, PREFIX
from discord.ext import commands


class EmbedGenerator:
    """
    Embeds for the bot.
    """

    def __init__(self) -> None:
        pass

    
    def now_playing(self, song: wavelink.Track) -> discord.Embed:
        # Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False)
        embed = discord.Embed(title=f"Now Playing: {song.title} :notes:",
                              description=f"By {song.author}",
                              color=discord.Color.green())
        duration = str(datetime.timedelta(seconds=song.duration)).lstrip("0:")
        if ':' not in duration:
            duration = f'0:{duration}'
        embed.add_field(name="Duration", value=duration, inline=True)
        return embed
    
    
    def song_queued(self, song: wavelink.Track, pos: int) -> discord.Embed:
        embed = discord.Embed(title="Song Queued",
                            description=song.title,
                            color=discord.Color.blue())
        embed.add_field(name="Position", value=pos, inline=True)
        return embed
    

    def playlist_added(self, count: int) -> discord.Embed:
        embed = discord.Embed(title="Update Queue",
                            description=f"{count} songs were added to the queue.",
                            color=discord.Color.blue())
        return embed
    


    def show_queue(self, vc: wavelink.Player) -> discord.Embed:
        pages = []
        songs = vc.queue.copy()
        song_count = 0
        desc = ""
        if (a := len(songs)/15) is int:
            total_pages = a
        else:
            total_pages = int(a) + 1

        total_songs = songs.count
        page_count = 1
        while not songs.is_empty:
            song = songs.get()
            song_count += 1
            try:
                duration = str(datetime.timedelta(seconds=song.duration)).lstrip("0:")
                if ':' not in duration:
                    duration = f'0:{duration}'

                desc += f"{song_count}. {song.title}[{duration}]\n"
            
            except AttributeError:
                desc += f"{song_count}. {song.title}\n"

            if song_count//15 == page_count:
                queue_embed_page = discord.Embed(
                    title=f"Queue | {total_songs} Tracks",
                    description=desc,
                    color=discord.Color.gold()
                )
                pages.append(queue_embed_page)
                desc = ""
                page_count += 1
                continue

        if desc:
            queue_embed_page = discord.Embed(
                title=f"Queue | {total_songs} Tracks",
                description=desc,
                color=discord.Color.gold()
            )
            pages.append(queue_embed_page)

        return pages
    

    def show_previous(self):
        desc=""
        song_count = 0
        for track in PREVIOUS_TRACKS:
            song_count += 1
            try:
                duration = str(datetime.timedelta(seconds=track.duration)).lstrip("0:")
                if ':' not in duration:
                    duration = f'0:{duration}'

                desc += f"{song_count}. {track.title}[{duration}]\n"
            
            except AttributeError:
                desc += f"{song_count}. {track.title}\n"

        embed = discord.Embed(
            title=f"Recently Played | {len(PREVIOUS_TRACKS)} Tracks",
            description=desc,
            color=discord.Color.brand_red()
        )

        return embed

    
    def show_help(self, ctx: commands.Context) -> discord.Embed:
        """Returns the help embed"""

        embed = discord.Embed(
            title=f"Vibe Bot | Command Prefix is {PREFIX}",
            description="A list of commands for the bot.",
            color=discord.Color.dark_orange()
        )
        embed.set_thumbnail(url=ctx.bot.user.avatar.url)
        embed.set_author(name="Creator: Nutty#6120 | Github: @Nutty1704")
        embed.add_field(
            name="play [p]",
            value="Plays the given song or playlist.",
            inline=False
        )
        embed.add_field(
            name="pause",
            value="Pauses the current song.",
            inline=False
        )
        embed.add_field(
            name="resume [res, r]",
            value="Resumes the current song.",
            inline=False
        )
        embed.add_field(
            name="skip",
            value="Skips the current song.",
            inline=False
        )
        embed.add_field(
            name="skipto [st]",
            value="Skips to the given song in the queue.",
            inline=False
        )
        embed.add_field(
            name="search",
            value="Searches for positon of the given song in the queue.",
            inline=False
        )
        embed.add_field(
            name="stop",
            value="Stops the current song and clears the queue.",
            inline=False
        )
        embed.add_field(
            name="queue [q]",
            value="Shows the current queue.",
            inline=False
        )
        embed.add_field(
            name="recentlyplayed [rp, sp, showprevious]",
            value="Shows the recently played songs.",
            inline=False
        )
        embed.add_field(
            name="nowplaying [np]",
            value="Shows the current song.",
            inline=False
        )
        embed.add_field(
            name="shuffle",
            value="Shuffles the current queue.",
            inline=False
        )
        embed.add_field(
            name="loop",
            value="Loops the current song.",
            inline=False
        )
        embed.add_field(
            name="loopqueue [lq]",
            value="Loops the current queue.",
            inline=False
        )
        embed.add_field(
            name="remove",
            value="Removes a song from the queue.",
            inline=False
        )
        embed.add_field(
            name="move",
            value="Moves a song in the queue.",
            inline=False
        )
        embed.add_field(
            name="help",
            value="Shows this message.",
            inline=False
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        return embed

            
