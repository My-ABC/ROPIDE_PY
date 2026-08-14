# syntax.py
"""
ROP 语法高亮定义 (Pygments Lexer)
用于在 Textual TUI 和其他支持 Pygments 的工具中高亮 ROP 代码
"""
from pygments.lexer import RegexLexer, bygroups, words
from pygments.token import (
    Comment, Keyword, Name, Number, Operator, String, Text,
    Punctuation, Whitespace
)

class RopLexer(RegexLexer):
    """
    ROP 语法高亮词法分析器
    支持 RopIDE 语法的所有元素
    """
    name = 'ROP'
    aliases = ['rop']
    filenames = ['*.rop']

    tokens = {
        'root': [
            # ============ 注释 ============
            (r'//.*$', Comment.Single),

            # ============ 常量定义 $name = value; ============
            (r'(\$[a-zA-Z0-9_-]+)(\s*=\s*)([0-9a-fA-F]+)(;)',
             bygroups(Name.Variable, Operator, Number.Hex, Operator)),

            # ============ Gadget 调用 #name; ============
            (r'(#-?[a-zA-Z0-9_-]+)(;)',
             bygroups(Keyword, Operator)),

            # ============ 标签 <name> 或 <-name> ============
            (r'(<-?[a-zA-Z0-9_-]+>)', Name.Label),

            # ============ 表达式 [expr] ============
            (r'\[', Operator, 'bracket'),

            # ============ 十六进制数据 (两位) ============
            (r'[0-9a-fA-F]{2}', Number.Hex),

            # ============ 空白 ============
            (r'\s+', Text),

            # ============ 其他符号 ============
            (r'[{}():,]', Punctuation),
            (r'.', Text),
        ],

        'bracket': [
            # ============ 表达式内部 ============
            (r'\]', Operator, '#pop'),
            (r'[a-zA-Z0-9_-]+', Name),
            (r'[+\-]', Operator),
            (r'\s+', Text),
        ]
    }


# ============ 便捷函数 ============

def highlight_rop_code(code: str) -> str:
    """
    高亮 ROP 代码，返回 ANSI 格式字符串
    """
    from pygments import highlight
    from pygments.formatters import Terminal256Formatter

    return highlight(code, RopLexer(), Terminal256Formatter(style='native'))


def highlight_rop_code_html(code: str) -> str:
    """
    高亮 ROP 代码，返回 HTML 格式字符串
    """
    from pygments import highlight
    from pygments.formatters import HtmlFormatter

    return highlight(code, RopLexer(), HtmlFormatter())