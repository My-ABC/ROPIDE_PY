import rop_parser as parser
import render
import rich
from rich.traceback import install
install()

if __name__ == '__main__':
    res = parser.parseRopInput(
    """
    <vpc++>
    #pop-er0; [$vpc++ - 2]
    """,
    [{"name": 'pop-er0', "addr": '121A8'}],
    {"leftStartAddress": "E9E0", "rightStartAddress": "D9D0"}
    )
    render.set_mode(True)
    rich.print(render.render_highlighted_code(res['highlightLines']))
    print(res['hexChars'])
    print(res['errorCount'])