from rich.text import Text

COLOR_MAP_DARK = {
    'comment': '#a0a0a0',
    'comment,single': '#a0a0a0',
    
    'hex': '#888888',

    'other': '#909090',
    
    'constant,name': '#66d9e8',
    'constant,equal': '#f8f8f2',
    'constant,value': '#a6e22e',
    'constant,warning': '#f1fa8c',
    
    'gadget': '#66d9ef',
    'gadget,closed': '#66d9ef',
    'gadget,warning': '#f1fa8c',
    
    'value': '#fd971f',
    'value,closed': '#fd971f',
    'value,warning': '#f1fa8c',
    
    'anchor': '#a6e22e',
    'anchor,closed': '#a6e22e',
    'anchor,warning': '#f1fa8c',
}

COLOR_MAP_LIGHT = {
    'comment': '#888888',
    'comment,single': '#888888',
    'hex': '#888888',
    'other': '#aaaaaa',
    'constant,name': '#0b7285',
    'constant,equal': '#212529',
    'constant,value': '#5c940d',
    'constant,warning': '#f59f00',
    'gadget': '#1864ab',
    'gadget,closed': '#1864ab',
    'gadget,warning': '#f59f00',
    'value': '#e67700',
    'value,closed': '#e67700',
    'value,warning': '#f59f00',
    'anchor': '#087f5b',
    'anchor,closed': '#087f5b',
    'anchor,warning': '#f59f00',
}

CURRENT_COLORS = COLOR_MAP_DARK

def set_mode(dark=True):
    global CURRENT_COLORS
    CURRENT_COLORS = COLOR_MAP_DARK if dark else COLOR_MAP_LIGHT

def render_highlighted_code(highlight_lines):
    full_text = Text()
    for line_spans in highlight_lines:
        line_text = Text()
        for span in line_spans:
            content = span.get('content', '')
            span_type = span.get('type', 'other')
            color = CURRENT_COLORS.get(span_type, '#e0e0e0')
            if 'warning' in span_type:
                line_text.append(content, style=f"{color} underline")
            else:
                line_text.append(content, style=color)
        full_text.append(line_text)
        full_text.append("\n")
    return full_text

__all__ = [
    "set_mode",
    "render_highlighted_code"
]