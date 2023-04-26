from discord.ext import commands
import discord
import wavelink
from utils import ytb_utils, play_utils, spotify_utils
from utils.embed_util import EmbedGenerator
from config import PREVIOUS_TRACKS

class Player(commands.Cog):

    eg = EmbedGenerator()

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Disconnects the bot when the last person leaves the voice channel."""
        # If the bot is not in a voice channel, return.
        if not member.guild.voice_client in self.bot.voice_clients:
            return

        if before.channel == after.channel:
            return
        
        # If the bot is in a voice channel, disconnect.
        if member == self.bot.user and not after.channel:
            vc = member.guild.voice_client
            await vc.disconnect()
            return

        # If the bot is the only one in the voice channel, disconnect.
        if len(before.channel.members) == 1 and before.channel.members[0] == self.bot.user:
            vc = member.guild.voice_client
            await vc.disconnect()
            return

    @commands.command(aliases=['p'])
    async def play(self, ctx: commands.Context, *, search):
        """Plays a song."""
        if not search:
            await ctx.reply('Please enter a search query.')
            return
        
        vc: wavelink.Player = await play_utils.get_voice_client(ctx)

        if not vc:
            return
        
        if "open.spotify" in search:
            await spotify_utils.play_spotify(ctx, vc, search)
        else:
            # Plays from YouTube
            await ytb_utils.play_ytb(ctx, vc, search)


    @commands.command(aliases=['pn'])
    async def playnow(self, ctx: commands.Context, *, search):
        """Plays a song now."""
        if not search:
            await ctx.reply('Please enter a search query.')
            return
        
        vc: wavelink.Player = await play_utils.get_voice_client(ctx)

        if not vc:
            return
        
        if "open.spotify" in search:
            await spotify_utils.play_spotify(ctx, vc, search, now=True)
        else:
            # Plays from YouTube
            await ytb_utils.play_ytb(ctx, vc, search, now=True)

    
    @commands.command()
    async def join(self, ctx: commands.Context):
        """Joins a voice channel."""
        return await play_utils.get_voice_client(ctx)


    @commands.command(aliases=['disconnect'])
    async def leave(self, ctx: commands.Context):
        """Leaves a voice channel."""
        vc = await play_utils.get_voice_client(ctx)

        # If the bot is not in a voice channel, return.
        if not vc:
            return
        
        # If the bot is in a voice channel, disconnect.
        await vc.disconnect()

    
    @commands.command()
    async def pause(self, ctx: commands.Context):
        """Pauses the current song."""
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return
        
        # If the bot is not playing anything, return.
        if not vc.is_playing:
            return await ctx.send('I am not playing anything.')
        
        # Pauses the song.
        await vc.pause()
        await ctx.send('**Paused**')

    @commands.command(aliases=['res', 'r'])
    async def resume(self, ctx: commands.Context):
        """Resumes the current song."""
        vc = await play_utils.get_voice_client(ctx)
        # If the bot is in a voice channel, resumes
        if vc:
            await vc.resume()
            await ctx.send('**Resumed**')

    @commands.command(aliases=['np'])
    async def now_playing(self, ctx: commands.Context):
        """Shows the current song."""
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return
        
        # If the bot is not playing anything, return
        if not vc.is_playing:
            return await ctx.send('I am not playing anything.')

        # Gets the current song.
        await ctx.reply(embed=self.eg.now_playing(vc.current))

    @commands.command()
    async def skip(self, ctx: commands.Context):
        """Skips the current song."""
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return
        
        # If the bot is not playing anything, return
        if not vc.is_playing:
            return await ctx.send('I am not playing anything.')

        # Skips the song.
        track = vc.current
        await vc.stop()
        await ctx.send(f'*Skipped* **{track.title}**')

    @commands.command(aliases=['st'])
    async def skipto(self, ctx: commands.Context, pos: int = False):
        """Skips to a position in the queue."""
        if not pos:
            return await ctx.reply('Please enter a position.')

        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return
        
        if vc.queue.is_empty:
            return await ctx.reply('*Queue is empty*')

        # If the position is out of range, return
        if pos > vc.queue.count or pos <= 0:
            return await ctx.reply(f'Position should be between 0 and {vc.queue.count}')
        
        # removing tracks from index 0 to index pos-2
        tracks = []
        try:
            # add songs to tracks until the queue is empty
            while True:
                tracks.append(vc.queue.get())
        except wavelink.errors.QueueEmpty:
            # play the song at position pos (index is pos - 1)
            song = tracks[pos - 1]
            await play_utils.play_now(ctx, vc, song)
            # add the rest of the songs to the queue
            if not pos >= len(tracks):
                tracks = tracks[pos:]
                # put the remaining tracks back in queue
                for track in tracks:
                    await vc.queue.put_wait(track)
        
        # sends a message informing about the successful skip
        await ctx.reply(f'**Skipped to position {pos}**')

    @commands.command()
    async def stop(self, ctx: commands.Context):
        """Stops the current song."""
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return
        
        # If the bot is not playing anything, return
        if not vc.is_playing:
            return await ctx.send('I am not playing anything.')

        # Clears the queue, disables loops and stops the song
        vc.queue.clear()
        play_utils.disable_loops(vc)
        await vc.stop()
        await ctx.send('**Stopped**')

    
    @commands.command(name="recentlyplayed", aliases=['sp', 'rp', 'showprevious'])
    async def previous(self, ctx: commands.Context):
        """
        Shows the recently played songs.
        """
        # if no song has been played yet, return
        if not PREVIOUS_TRACKS:
            await ctx.reply("Nothing has been played yet")
            return
        # sends the embed with list of recently played songs
        await ctx.send(embed=self.eg.show_previous())

    @commands.command(name='playlast', aliases=['pl'])
    async def play_last(self, ctx: commands.Context, pos: int = 1):
        """
        Plays the selected song from recently played songs.
        """
        # if no song has been played yet, return
        if not PREVIOUS_TRACKS:
            await ctx.reply("Nothing has been played yet")
            return
        # gets the voice client
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return
        
        # if the position is out of range, return
        if pos > len(PREVIOUS_TRACKS) or pos <= 0:
            await ctx.reply(f"Position should be between 1 and {len(PREVIOUS_TRACKS)}")
            return
        
        # plays the song at given 
        track = PREVIOUS_TRACKS.pop(pos-1)
        await self.playnow(ctx, search=track.uri)


    @commands.command(aliases=['rem'])
    async def remove(self, ctx: commands.Context, pos: int = False):
        """Removes a song from the queue."""

        # If the position is not provided, return
        if not pos:
            return await ctx.reply('Please provide a position.')
        
        # Gets the voice client
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return
        
        # If the queue is empty, return
        if vc.queue.is_empty:
            return await ctx.reply('*Queue is empty*')
        
        # If the position is out of range, return
        if pos > vc.queue.count or pos <= 0:
            return await ctx.reply(f'Position should be between 1 and {vc.queue.count}')
        
        # removing tracks at the given position
        track = vc.queue[pos-1]
        del vc.queue[pos-1]
        await ctx.reply(f'Removed **{track.title}** from the queue.')


    @commands.command()
    async def search(self, ctx: commands.Context, *, title: str = ""):
        """Searches for a song in the queue using the given keywords."""
        # If the title is not provided, return
        if not title:
            await ctx.reply('Please enter a title.')

        # Gets the voice client
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return

        # filter the key words from the title
        words = title.split(' ')
        words = [word for word in words if word not in ['the', 'a', 'an']]

        # search for the title in the queue
        for i in range(0, vc.queue.count):
            # if the title is found, return the position
            for word in words:
                if not word.lower() in vc.queue[i].title.lower():
                    break
            else:
                await ctx.reply(f'**{vc.queue[i].title}** is at position {i+1}')
                return
            
        # if the title is not found, return
        await ctx.reply(f'No song found with the title **{title}**')


    @commands.command()
    async def move(self, ctx: commands.Context, pos: int = -1, new_pos: int = -1):
        """Moves a song from one position to another."""
        # If the position is not provided, return
        if pos == -1 or new_pos == -1:
            return await ctx.reply('Please enter a position.')
        
        # Gets the voice client
        vc = await play_utils.get_voice_client(ctx)
        if not vc:
            return
        
        # If the queue is empty, return
        if vc.queue.is_empty:
            return await ctx.reply('*Queue is empty*')
        
        # If the position is out of range, return
        if pos > vc.queue.count or pos <= 0 or new_pos > vc.queue.count or new_pos <= 0:
            return await ctx.reply(f'Positions should be between 1 and {vc.queue.count}')
        
        track = vc.queue[pos-1]

        # if the position is same as the new position, return
        if pos == new_pos:
            return await ctx.reply(f'**{track.title}** is already at position {pos}.')

        # move the song at position pos to position new_pos
        del vc.queue[pos-1]
        vc.queue.put_at_index(new_pos-1, track)
        await ctx.reply(f'Moved **{track.title}** to position {new_pos}.')

async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot))