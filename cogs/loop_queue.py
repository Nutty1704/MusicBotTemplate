from discord.ext import commands
import wavelink
from utils import queue_utils, play_utils
import config
from utils.embed_util import EmbedGenerator
import Paginator

class LoopQ(commands.Cog):

    """"
    Queue and Loop commands.
    """

    eg = EmbedGenerator()

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        """
        Listens for when a track ends.
        """
        ctx = player.ctx
        vc = player.guild.voice_client

        # If the track is on loop, play it again.
        if vc.loop:
            return await play_utils.play_track(ctx, vc, track)

        # Add the song to history
        queue_utils.add_to_previous_queue(track)

        # If the queue is not empty, play the next song.
        if not vc.queue.is_empty:
            next_song = vc.queue.get()
            await play_utils.play_track(ctx, vc, next_song)

        elif vc.loopq:
            vc.queue = config.LOOPQ.copy()
            next_song = vc.queue.get()
            await play_utils.play_track(ctx, vc, next_song)

        # If the queue is empty, stop the player.
        else:
            await vc.stop()
            await ctx.send('**Queue has concluded.**')

    
    @commands.command(aliases=['lq'])
    async def loopq(self, ctx: commands.Context):
        """Loops the queue."""
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return

        # If the bot is not playing anything, return.
        if not vc.is_playing:
            return await ctx.send('I am not playing anything.')

        # If the song is on loop, turn it off.
        if vc.loopq:
            vc.loopq = False
            config.LOOPQ = None
            await ctx.send('*Loop disabled*')
        # If the song is not on loop, turn it on.
        else:
            vc.loopq = True
            current_track = play_utils.get_currenly_playing(vc)
            config.LOOPQ = vc.queue.copy()
            config.LOOPQ.put_at_front(current_track)
            await ctx.send('**Queue is now on loop :repeat:**')

    @commands.command(aliases=['l'])
    async def loop(self, ctx: commands.Context):
        """Loops the current song."""
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return

        # If the bot is not playing anything, return.
        if not vc.is_playing:
            return await ctx.send('I am not playing anything.')

        # If the song is on loop, turn it off.
        if vc.loop:
            vc.loop = False
            await ctx.send('**Loop disabled**')
        # If the song is not on loop, turn it on.
        else:
            vc.loop = True
            current_track = play_utils.get_currenly_playing(vc)
            await ctx.send(f'**Looping {current_track.title}:repeat:**')


    @commands.command(aliases=['cq'])
    async def clear(self, ctx: commands.Context):
        """Clears the queue."""
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return
        
        # If the bot is not playing anything, return.
        if not vc.is_playing:
            return await ctx.send('I am not playing anything.')

        # Clears the queue.
        vc.queue.clear()
        await ctx.send('**Cleared the queue**')


    @commands.command(aliases=['q'])
    async def queue(self, ctx: commands.Context):
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return
        
        # If the queue is empty, return.
        if vc.queue.is_empty:
            return await ctx.send('Queue is empty')
        
        # gets the pages in the queue embed
        pages = self.eg.show_queue(vc)
        await Paginator.Simple(timeout=20).start(ctx, pages=pages)
        

    
    @commands.command()
    async def shuffle(self, ctx: commands.Context):
        vc = await play_utils.get_voice_client(ctx)

        if not vc:
            return
        
        if vc.queue.is_empty:
            return await ctx.send('The queue is empty.')
        
        await queue_utils.shuffle(vc.queue)
        await ctx.send('**Queue has been shuffled**')


async def setup(bot: commands.Bot):
    await bot.add_cog(LoopQ(bot))