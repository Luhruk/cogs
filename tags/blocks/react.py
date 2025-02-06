from typing import Optional

from TagScriptEngine import Block, Context


class ReactBlock(Block):
    """
    The react block will react with up to 5 emoji to the tag response message.
    If the name used is ``reactu``, it will react to the tag invocation instead.
    The given emoji can be custom or unicode emoji. Emojis can be split with ",".

    The block accepts emojis being passed to the parameter or the payload, but not both.

    **Usage:** ``{react(<emoji,emoji>):[emoji,emoji]}``

    **Aliases:** ``reactu``

    **Payload:** emoji

    **Parameter:** emoji

    **Examples:** ::

        {react(🅱️)}
        {react(🍎,🍏)}
        {react(<:kappa:754146174843355146>)}
        {reactu:🅱️}
    """

    ACCEPTED_NAMES = ("react", "reactu")

    def will_accept(self, ctx: Context) -> bool:
        if not (ctx.verb.parameter or ctx.verb.payload):
            return False
        return super().will_accept(ctx)

    def process(self, ctx: Context) -> Optional[str]:
        emojis = ctx.verb.parameter or ctx.verb.payload
        ctx.response.actions[ctx.verb.declaration.lower()] = [
            arg.strip() for arg in emojis.split(",")[:5]
        ]
        return ""