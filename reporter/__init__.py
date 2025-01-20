from .reporter import Reporter

def setup(bot):
    bot.add_cog(Reporter(bot))
