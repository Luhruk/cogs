from redbot.core import commands
from redbot.core import Config

class CharacterCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 458748958)
        self.config.register_user(characters={}, active_character="None")

    @commands.command()
    async def create(self, ctx, name: str, race: str, gender: str):
        """Create a new character."""
        user_data = await self.config.user(ctx.author).all()
        if name in user_data.get("characters", {}):
            await ctx.send(f"Character '{name}' already exists.")
            return

        # Create character with basic stats
        await self.config.user(ctx.author).characters.set_raw(name, value={"race": race, "gender": gender, "level": 1})
        await ctx.send(f"Character '{name}' created!")

    @commands.command()
    async def setactive(self, ctx, character_name: str):
        """Set a character as active."""
        user_data = await self.config.user(ctx.author).all()
        
        # Check if the character exists
        if character_name not in user_data.get("characters", {}):
            await ctx.send(f"Character '{character_name}' not found.")
            return
        
        # Set the active character
        await self.config.user(ctx.author).active_character.set(character_name)
        await ctx.send(f"Character '{character_name}' is now active!")

    @commands.command()
    async def info(self, ctx):
        """View your character's information."""
        user_data = await self.config.user(ctx.author).all()
        
        active_character = user_data.get("active_character", "None")
        characters = user_data.get("characters", {})
        
        if not characters:
            await ctx.send("You have no characters yet. Use `.char create` to create one.")
            return
        
        char_info = f"Active Character: {active_character}\n\n"
        char_info += "\n".join([f"{name}: Level {data['level']}" for name, data in characters.items()])
        
        await ctx.send(char_info)

    @commands.command()
    async def list(self, ctx):
        """List all characters."""
        user_data = await self.config.user(ctx.author).all()
        
        characters = user_data.get("characters", {})
        if not characters:
            await ctx.send("You have no characters yet. Use `.char create` to create one.")
            return
        
        char_list = "\n".join([f"{name}: Level {data['level']}" for name, data in characters.items()])
        await ctx.send(f"Your characters:\n{char_list}")
