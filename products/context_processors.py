def homeware_categories(request):
    """
    Provides homeware categories as a context variable across all templates
    """
    homeware_cats = ["mugs", "coasters", "skateboard_decks"]

    return {
        "homeware_categories": homeware_cats,
    }
