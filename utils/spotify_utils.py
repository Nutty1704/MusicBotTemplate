import wavelink
from wavelink.ext import spotify
from utils.play_utils import play_track, play_now, disable_loops
from utils.embed_util import EmbedGenerator
from discord.ext import commands
import config

eg = EmbedGenerator()

async def play_spotify(ctx: commands.Context, vc: wavelink.Player, search: str, now=False):
    try:
        decoded = spotify.decode_url(search)
    except:
        return await ctx.reply(config.INVALID_INPUT)
    
    # If the search returns None i.e. fails to find a song/playlist/album
    if not decoded:
        return await ctx.reply(config.INVALID_INPUT)

    # Gets the id and type of the search
    type, id = decoded['type'], decoded['id']

    # If the search is a song
    if type == spotify.SpotifySearchType.track:
        await play_spotify_track(ctx, vc, search, now)

    # If the search is a playlist or album
    else:
        if now:
            return await ctx.reply("Playnow command can only take in single songs.")
        await add_tracks_from_collection(ctx, vc, search)
        


async def play_spotify_track(ctx: commands.Context, vc: wavelink.Player, query: str, now: bool):
        # gets the song
        song = await spotify.SpotifyTrack.search(query=query, return_first=True)
        song.uri = query

        # If the bot is not playing anything, play the song
        if not vc.is_playing():
            return await play_track(ctx, vc, song)
        
        # If play now is enabled, play the song irrespective of what the bot is playing
        if now:
            disable_loops(vc)
            return await play_now(ctx, vc, song)

        # If the bot is playing something, add the song to the queue
        await vc.queue.put_wait(song)
        # Sends the embed
        embed = eg.song_queued(song, vc.queue.count)
        await ctx.send(embed=embed)


async def add_tracks_from_collection(ctx: commands.Context, vc: wavelink.Player, query: str):
    count = 0
    temp_msg = await ctx.send('Loading tracks...')

    # gets the tracks from the playlist or album
    async for song in spotify.SpotifyTrack.iterator(query=query):
        # If the bot is not playing anything, play the first song
        if not vc.is_playing():
            await play_track(ctx, vc, song)
            continue
        
        # If play now is not enabled, add the song to the back of the queue, else add it to the front
        try:
            await vc.queue.put_wait(song)
        except:
            continue

        if vc.loopq:
            await config.LOOPQ.put_wait(song)

        count += 1

    # Sends the embed  
    embed = eg.playlist_added(count)
    await temp_msg.delete()
    await ctx.send(embed=embed)
