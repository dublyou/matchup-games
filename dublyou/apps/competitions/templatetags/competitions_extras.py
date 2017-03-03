from django import template

register = template.Library()


@register.filter
def place_string(place):
    last_digit = int(str(place)[-1])
    endings = {1: "st", 2: "nd", 3: "rd"}
    ending = endings[last_digit] \
        if place not in range(11, 14) and last_digit in endings \
        else "th"
    return "{}{}".format(place, ending)


@register.filter
def multiply(value, multiplier):
    return value*multiplier


@register.filter
def divide(numerator, denominator):
    return numerator / denominator


@register.simple_tag
def bracket_connector(round_num, size, game1, game2):
    size = size or round_num
    params = {"round_num": round_num,
              "width": 10,
              "half_width": 5,
              "size": size}
    connector_html = ""
    if round_num > 0:
        params["height"] = (29 + 5) * (2 ** size)
        params["half_height"] = params["height"]/2
        params["top"] = (-params["height"] / 2) + 29
        connector_html = '<svg height="{height}" width="{width}" style="position:absolute;left:-{half_width}px;top:{top}px" class="connect round-{round_num} game-{game1}">'.format(**params)
        connector_html += '<line x1={half_width} y1={half_height} x2={width} y2={half_height}/>'.format(**params)
        connector_html += '<line class="top" x1={half_width} y1="0" x2={half_width} y2={half_height}/>'.format(**params)
        connector_html += '<line class="top" x1="0" y1="0" x2={half_width} y2="0"/></svg>'.format(**params)
        connector_html += '<svg height={height} width={width} style="position:absolute;left:-{width}px;top:{top}px" class="connect round-{round_num} game-{game2}>'.format(**params)
        connector_html += '<line x1={half_width} y1={half_height x2={width} y2={half_height}/>'.format(**params)
        connector_html += '<line class="bottom" x1={half_width} y1={half_height} x2={half_width} y2={height}/>'.format(**params)
        connector_html += '<line class="bottom" x1="0" y1={height} x2={half_width} y2={height}/></svg>'.format(**params)
    return connector_html

