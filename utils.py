from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import Python3Lexer, JavascriptLexer, JavaLexer, CppLexer, GoLexer
from pygments.style import Style
from pygments.token import Token, Comment, Keyword, Name, String, Number, Operator


# 🎨 Define a custom style
class CustomStyle(Style):
    background_color = "#282a36"
    default_style = ""

    styles = {
        Token:              "#f8f8f2",
        Comment:            "italic #6272a4",
        Keyword:            "bold #ff79c6",
        Name:               "#f8f8f2",
        Name.Function:      "#50fa7b",
        Name.Class:         "bold #50fa7b",
        String:             "#f1fa8c",
        Number:             "#bd93f9",
        Operator:           "#ff79c6",
    }


def get_syntax_highlighted_code(code: str, language: str = "python") -> str:
    """
    Apply syntax highlighting to code with specified language.
    Returns highlighted HTML code block.
    """
    lexer_mapping = {
        'python': Python3Lexer(),
        'javascript': JavascriptLexer(),
        'java': JavaLexer(),
        'c++': CppLexer(),
        'go': GoLexer()
    }

    try:
        lexer = lexer_mapping.get(language.lower(), Python3Lexer())
        formatter = HtmlFormatter(
            style=CustomStyle,   # use our custom style
            noclasses=True,
            nobackground=True,
            linenos=True,
            lineseparator="<br>"
        )

        highlighted = highlight(code, lexer, formatter)

        return f"""
        <div style="
            background: #282a36; 
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            overflow-x: auto;
            font-family: 'Fira Code', 'Courier New', monospace;
            line-height: 1.5;
            color: #f8f8f2;
        ">{highlighted}</div>
        """

    except Exception as e:
        print(f"Highlighting error: {e}")
        return f"""
        <div style="
            background: #282a36;
            color: #f8f8f2;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-family: monospace;
            white-space: pre;
            overflow-x: auto;
        ">{code}</div>
        """
