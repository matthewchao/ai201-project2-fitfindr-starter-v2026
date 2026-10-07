"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re
import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── query parsing ─────────────────────────────────────────────────────────────

# Sizes a user is likely to type. Matched as whole words so that the "M" in
# "Medium Wash" or the "L" in "L/XL" can't be mistaken for a request.
_SIZE_WORDS = r"XXS|XS|S|M|L|XL|XXL"

_PRICE_RE = re.compile(r"(?:under|below|less than|max|up to)?\s*\$\s*(\d+(?:\.\d+)?)", re.I)
_SIZE_RE = re.compile(rf"\b(?:in\s+)?size\s+({_SIZE_WORDS}|(?:\bUS\s*)?\d+(?:\.\d+)?|W\d+)\b", re.I)
_BARE_SIZE_RE = re.compile(rf",\s*({_SIZE_WORDS})\s*$", re.I)


def parse_query(query: str) -> dict:
    """
    Pull a description, a size, and a price ceiling out of what the user typed.

    Regex rather than a model call: costs nothing, returns the same answer
    every time, and keeps failure modes transparently diagnosable.

    Returns a dict with keys:
        - description (str)
        - size (str or None)
        - max_price (float or None)
    """
    text = query or ""

    max_price = None
    price_match = _PRICE_RE.search(text)
    if price_match:
        max_price = float(price_match.group(1))
        text = text[: price_match.start()] + " " + text[price_match.end() :]

    size = None
    size_match = _SIZE_RE.search(text) or _BARE_SIZE_RE.search(text)
    if size_match:
        size = re.sub(r"\s+", " ", size_match.group(1)).strip().upper()
        text = text[: size_match.start()] + " " + text[size_match.end() :]

    description = re.sub(r"[,\s]+", " ", text).strip(" ,")
    return {"description": description, "size": size, "max_price": max_price}


def _nothing_found_message(parsed: dict) -> str:
    """
    What to say when the search comes back empty.

    Names the parameters that were actually in play and suggests concrete
    adjustments the user can make.
    """
    tried = [f"description {parsed.get('description')!r}"]
    if parsed.get("size"):
        tried.append(f"size {parsed['size']}")
    if parsed.get("max_price") is not None:
        tried.append(f"under ${parsed['max_price']:g}")

    suggestions = ["try broader words — 'jacket' finds more than 'cropped corduroy jacket'"]
    if parsed.get("size"):
        suggestions.append("drop the size, or try a neighbouring one")
    if parsed.get("max_price") is not None:
        suggestions.append(f"raise the price ceiling above ${parsed['max_price']:g}")

    return (
        "Nothing in the listings matched " + ", ".join(tried) + ".\n"
        "Things to change: " + "; ".join(suggestions) + "."
    )


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. Check session["error"] first — if it isn't None,
        the run ended early and the later fields will still be None.
    """
    session = new_session(query, wardrobe)
    steps = 0

    # 1. Parse query
    steps += 1
    trace.check_iterations(steps)
    session["parsed"] = parse_query(query)

    # 2. Search listings
    steps += 1
    trace.check_iterations(steps)
    session["search_results"] = search_listings(
        description=session["parsed"].get("description", ""),
        size=session["parsed"].get("size"),
        max_price=session["parsed"].get("max_price"),
    )

    # ── THE BRANCH ────────────────────────────────────────────────────────
    if not session["search_results"]:
        session["error"] = _nothing_found_message(session["parsed"])
        return session

    # 3. Choose top item
    steps += 1
    trace.check_iterations(steps)
    session["selected_item"] = session["search_results"][0]

    # 4. Suggest outfit
    steps += 1
    trace.check_iterations(steps)
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"], session["wardrobe"]
    )

    # 5. Create fit card
    steps += 1
    trace.check_iterations(steps)
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"], session["selected_item"]
    )

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
