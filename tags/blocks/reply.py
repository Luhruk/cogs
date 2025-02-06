from typing import Optional

from TagScriptEngine import Block, Context, helper_parse_if


class ReplyBlock(Block):
    """
    Reply blocks are conditional components that trigger bot responses to be replied when the specified parameter is set to ``True``.
    If no parameter is provided ``{reply}``, it'll default to ``True``.

    **Usage:** ``{reply([bool])}``

    **Payload:** None

    **Parameter:** bool, None

    **Examples:** ::

        {reply}
        {reply(False)}
    """

    def will_accept(self, ctx: Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return any([dec == "reply", dec == "respond"])

    def process(self, ctx: Context) -> Optional[str]:
        if "reply" in ctx.response.actions.keys():
            return None
        if ctx.verb.parameter is None:
            value = True
        else:
            value = helper_parse_if(ctx.verb.parameter)
        ctx.response.actions["reply"] = value
        return ""