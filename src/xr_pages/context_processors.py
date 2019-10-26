def svg_icons_context_processor(request):
    """
    Provide an empty set, that will be filled with the name of the icon, that was embedded.

    This is relevant for the svg_icon template tag.
    """
    return {"_embedded_svg_icons": set()}
