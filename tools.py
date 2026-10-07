"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config
import re
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

_STOPWORDS = {
    "a", "an", "and", "the", "for", "with", "under", "over", "in", "of",
    "to", "on", "at", "by", "from", "looking", "want", "need", "find"
}


def _keywords(text: str) -> set[str]:
    """Lowercase words worth matching on, stopwords removed."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}


def _size_tokens(size: str) -> set[str]:
    """
    Normalize a size string into discrete tokens for comparison.
    Drops parentheticals like '(oversized)' and splits composite sizes like 'S/M'.
    """
    cleaned = re.sub(r"\([^)]*\)", " ", size or "").upper()
    tokens = set()
    for part in cleaned.split("/"):
        p = part.strip()
        if not p:
            continue
        tokens.add(p)
        for sub in p.split():
            tokens.add(sub)
    return tokens


def _size_matches(wanted: str, listing_size: str) -> bool:
    """
    Determine if a requested size matches a listing's size.
    Case-insensitive, handles composite sizes (e.g., 'M' matches 'S/M' and 'M/L'),
    and treats 'ONE SIZE' listings as universal matches.
    """
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True
    wanted_tokens = _size_tokens(wanted)
    return bool(wanted_tokens & listing_tokens)


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        Returns an empty list [] when nothing matches.
    """
    all_listings = load_listings()
    query_words = _keywords(description)
    scored_matches: list[tuple[int, dict]] = []

    for item in all_listings:
        # 1. Filter by price ceiling
        item_price = item.get("price")
        if max_price is not None and item_price is not None:
            if item_price > max_price:
                continue

        # 2. Filter by size
        if size is not None:
            if not _size_matches(size, item.get("size", "")):
                continue

        # 3. Score keyword relevance across fields
        if query_words:
            title_words = _keywords(item.get("title", ""))
            tags_words = _keywords(" ".join(item.get("style_tags", [])))
            desc_words = _keywords(item.get("description", ""))
            cat_words = _keywords(item.get("category", ""))
            color_words = _keywords(" ".join(item.get("colors", [])))
            brand_words = _keywords(item.get("brand") or "")

            score = 0
            for kw in query_words:
                if kw in title_words:
                    score += 4
                if kw in tags_words:
                    score += 3
                if kw in desc_words:
                    score += 2
                if kw in cat_words:
                    score += 2
                if kw in color_words:
                    score += 1
                if kw in brand_words:
                    score += 1

            if score == 0:
                continue
        else:
            score = 1

        scored_matches.append((score, item))

    # Sort by relevance score descending, then by price ascending
    scored_matches.sort(key=lambda pair: (-pair[0], pair[1].get("price", 0)))

    limit = getattr(config, "SEARCH_RESULT_LIMIT", 10)
    return [item for _, item in scored_matches[:limit]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  May be empty.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, returns general styling advice rather than
        raising or returning "".
    """
    wardrobe_items = (wardrobe or {}).get("items") or []

    item_title = new_item.get("title", "thrifted item")
    item_category = new_item.get("category", "")
    item_colors = ", ".join(new_item.get("colors", []))
    item_tags = ", ".join(new_item.get("style_tags", []))
    item_desc = new_item.get("description", "")

    if not wardrobe_items:
        prompt = (
            "You are FitFindr, an expert personal thrift stylist.\n"
            f"The user is considering buying this piece:\n"
            f"- Title: {item_title}\n"
            f"- Category: {item_category}\n"
            f"- Colors: {item_colors}\n"
            f"- Style Tags: {item_tags}\n"
            f"- Description: {item_desc}\n\n"
            "Provide 1 or 2 creative styling suggestions and outfit ideas for how to wear this item. "
            "Focus on complementary silhouettes, colors, and aesthetics. "
            "Give direct, inspiring styling recommendations without mentioning empty closets or missing items."
        )
    else:
        wardrobe_lines = []
        for w in wardrobe_items:
            w_colors = ", ".join(w.get("colors", []))
            wardrobe_lines.append(f"- {w.get('name', 'Unknown')} ({w.get('category', '')}, {w_colors})")
        wardrobe_text = "\n".join(wardrobe_lines)

        prompt = (
            "You are FitFindr, an expert personal thrift stylist.\n"
            f"The user is considering buying this thrifted piece:\n"
            f"- Title: {item_title}\n"
            f"- Category: {item_category}\n"
            f"- Colors: {item_colors}\n"
            f"- Style Tags: {item_tags}\n"
            f"- Description: {item_desc}\n\n"
            "The user owns the following pieces in their existing wardrobe:\n"
            f"{wardrobe_text}\n\n"
            "Suggest 1 or 2 specific outfit pairings combining the thrifted item with pieces from their wardrobe. "
            "Explain how the pieces work together into a cohesive look."
        )

    response = generate(prompt)
    return response.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A short, authentic social media caption.
        If `outfit` is empty or whitespace, returns a descriptive fallback.
    """
    price_val = new_item.get("price")
    price_str = f"${price_val:g}" if isinstance(price_val, (int, float)) else ""
    platform = new_item.get("platform", "thrift store")
    title = new_item.get("title", "vintage piece")

    if not outfit or not outfit.strip():
        return f"Scored this {title} for {price_str} on {platform}! Excited to style it into fresh fits."

    prompt = (
        "You are FitFindr. Write an authentic social media caption (like an Instagram or TikTok post) "
        "showing off this thrift find and how to style it.\n\n"
        f"Item: {title}\n"
        f"Price: {price_str}\n"
        f"Platform: {platform}\n"
        f"Styling ideas: {outfit}\n\n"
        "Requirements:\n"
        "- Sound like a real person sharing a thrifting victory, not a corporate product listing.\n"
        f"- Mention the item name, the price ({price_str}), and the platform ({platform})."
    )

    response = generate(prompt)
    return response.strip()
