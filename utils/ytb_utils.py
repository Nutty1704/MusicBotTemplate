from discord.ext import commands
import wavelink
import config
from utils.embed_util import EmbedGenerator
from utils.play_utils import play_track, play_now, disable_loops
import pytube


eg = EmbedGenerator()


async def play_ytb(ctx: commands.Context, vc: wavelink.Player, search: str, now=False):
    if "youtube.com/playlist" in search:
        if now:
            return await ctx.reply("Playnow command can only take in single songs.")
        await add_playlist(ctx, vc, search)
    elif "youtube.com/watch" in search:
        search = form_query(search)
        
    await add_song(ctx, vc, search, now)


def form_query(search: str):
    yt = pytube.YouTube(search)
    return f"{yt.title} {yt.author}"



async def add_playlist(ctx: commands.Context, vc: wavelink.Player, search: str):
    """
    Adds a playlist to the queue.
    """
    # tries to get the tracks from the playlist
    try:
        playlist = await wavelink.YouTubePlaylist.search(query=search)
        tracks = playlist.tracks
    # if the playlist is not found, return
    except wavelink.exceptions.NoTracksFound:
        return await ctx.reply(config.INVALID_INPUT)
    
    else:
        count = 0
        temp = await ctx.send('Loading tracks...')
        for track in tracks:
            # If the bot is not playing anything, play the first song
            if not vc.is_playing():
                await play_track(ctx, vc, track)
                continue

            try:
                await vc.queue.put_wait(track)
            except:
                continue

            # update cache queue if loopq is enabled
            if vc.loopq:
                await config.LOOPQ.put_wait(track)
            count += 1

        await temp.delete()
        await ctx.send(embed=eg.playlist_added(count))


async def add_song(ctx: commands.Context, vc: wavelink.Player, search: str, now: bool):
    """
    Adds a song to the queue or plays it
    """
    # Searches for the song
    try:
        track = await wavelink.YouTubeTrack.search(query=search, return_first=True)
    # sends a message if the song is not found
    except wavelink.exceptions.NoTracksFound:
        return await ctx.reply(config.INVALID_INPUT)
    else:
        # If the bot is not playing anything, play the song
        if not vc.is_playing():
            return await play_track(ctx, vc, track)
        
        # If play now is enabled, play the song irrespective of what the bot is playing
        if now:
            disable_loops(vc)
            return await play_now(ctx, vc, track)

        
        # If the bot is playing something, add the song to the queue
        await vc.queue.put_wait(track)
        await ctx.send(embed=eg.song_queued(track, vc.queue.count))

        # If loopq is enabled, add the song to the cahce queue
        if vc.loopq:
            await config.LOOPQ.put_wait(track)