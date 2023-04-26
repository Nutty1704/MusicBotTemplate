from discord.ext import commands
import discord
import wavelink
from wavelink.ext import spotify
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET_ID, PREFIX


class Setup(commands.Cog):
    """
    Basic commands for the bot.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        async def node_connect():
            await self.bot.wait_until_ready()

            nodes = [
                {"host": "eu-lavalink.lexnet.cc", "port": 443,
                    "password": "lexn3tl@val!nk", "https": True, },
                {"host": "lavalink.devamop.in", "port": 443,
                    "password": "DevamOP", "https": True},
                {"host": "lavalink.lexnet.cc", "port": 443,
                    "password": "lexn3tl@val!nk", "https": True},
                {"host": "suki.nathan.to", "port": 443,
                    "password": "adowbongmanacc", "https": True}
            ]

            for node in nodes:
                await wavelink.NodePool.create_node(bot=self.bot,
                                                    spotify_client=spotify.SpotifyClient(client_id=SPOTIFY_CLIENT_ID,
                                                                                         client_secret=SPOTIFY_CLIENT_SECRET_ID),
                                                    **node)

        self.bot.loop.create_task(node_connect())
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{PREFIX}help"))
        print(f'{self.bot.user.name} is ready!')

    @commands.Cog.listener()
    async def on_wavelink_node_ready(node: wavelink.Node):
        print(f'Node {node.identifier} is ready!')


async def setup(bot):
    await bot.add_cog(Setup(bot))
