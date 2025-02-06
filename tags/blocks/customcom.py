import re

from TagScriptEngine import Block, Context

CONVERTER_RE = re.compile(r"(?i)(\d{1,2})(?:\.[a-z]+)?(?::[a-z]+)?")


class ContextVariableBlock(Block):
    def will_accept(self, ctx: Context) -> bool:
        dec = ctx.verb.declaration.lower().split(".", 1)[0]
        return dec in ("author", "channel", "server", "guild")

    def process(self, ctx: Context) -> str:
        dec = ctx.verb.declaration.lower().split(".", 1)
        parameter = f"({dec[1]})" if len(dec) == 2 else ""
        return "{%s%s}" % (dec[0], parameter)


class ConverterBlock(Block):
    def will_accept(self, ctx: Context) -> bool:
        return bool(CONVERTER_RE.match(ctx.verb.declaration))

    def process(self, ctx: Context) -> str:
        match = CONVERTER_RE.match(ctx.verb.declaration)
        num = int(match.group(1)) + 1
        return "{args(%s)}" % num