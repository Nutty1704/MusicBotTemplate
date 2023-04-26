from discord.ext import commands
from utils.embed_util import EmbedGenerator

class Basics(commands.Cog):
    """Basic commands for the bot."""

    eg = EmbedGenerator()

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Returns the bot's latency in milliseconds."""
        await ctx.reply(f'*Pong! {round(self.bot.latency * 1000)}ms*')

    @commands.command()
    async def help(self, ctx: commands.Context):
        """Show the help embed"""
        embed = self.eg.show_help(ctx)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Basics(bot))