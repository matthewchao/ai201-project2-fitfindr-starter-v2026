# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is a thrift shopping agent that searches listings, styles finds with clothes you already own, and writes social captions to show them off. A user asks for what they want in plain language with an optional size and price limit (e.g., 'vintage graphic tee under $30, size M'). When matching items are found, FitFindr picks the top result, pairs it with pieces from the user's existing wardrobe, and creates a ready-to-post fit card. If no listings match, the agent stops early and explains what filters or keywords to change instead of failing blindly.



---

## Tool Inventory

### `search_listings`

- **What it does:** Searches the listings dataset for the items which satisfy the max_price and size constraints if provided, and which best match the description.
- **Inputs:** `description` (`str`) is keywords describing the desired item, `size` (`str | None`) is the clothing size to filter on, and `max_price` (`float | None`) is the budget limit; the latter two inputs are optional.
- **Returns:** Returns a `list[dict]`, where each dict represents a matching clothing piece in the listings data with fields `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.
- **When it has nothing:** It returns an empty list, `[]`.

### `suggest_outfit`

- **What it does:** Suggests one or two outfit combinations pairing a thrifted item with pieces the user already owns in their wardrobe.
- **Inputs:** `new_item` (`dict`) is a listing dictionary representing the thrifted piece under consideration, and `wardrobe` (`dict`) is a dictionary containing an `'items'` key holding a list of wardrobe item dicts.
- **Returns:** Returns a non-empty `str` containing outfit recommendations naming specific matching pieces from the user's wardrobe.
- **When it has nothing:** When the user's wardrobe is empty, i.e. the wardrobe's `'items'` list is empty, it returns a non-empty `str` providing general styling advice for the item rather than raising an error or returning an empty string.

### `create_fit_card`

- **What it does:** Generates a short social media caption about a thrifted find and its suggested outfit.
- **Inputs:** `outfit` (`str`) is the outfit suggestion string (typically from `suggest_outfit`), and `new_item` (`dict`) is the listing dictionary for the thrifted item.
- **Returns:** Returns a `str` containing a two-to-four sentence caption formatted like a real social media post, mentioning the item, its price, and its platform once each while conveying the aesthetic vibe.
- **When it has nothing:** When `outfit` is empty or contains only whitespace, it returns a non-empty `str` with a descriptive fallback message rather than raising an exception.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, write an actionable message to `session["error"]` naming search parameters the user could adjust (such as increasing the price ceiling, removing size filters, or broadening keywords) and stop execution before calling `suggest_outfit`. Otherwise, save `search_results[0]` into `session["selected_item"]` and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex matching on price ceilings (e.g. `under $X` or `max $X`) and sizes (e.g. `size X` or standalone size tokens like `S`, `M`, `L`, `XL`), with remaining terms cleaned of punctuation and stopwords to form the `description` keyword query.

**What moves through the session:**
1. `query` & `wardrobe` (set initially in `new_session`)
2. `parsed` (populated with extracted `description`, `size`, `max_price`)
3. `search_results` (populated by `search_listings`)
4. Branch decision:
   - If empty: `error` is set, and the loop returns early.
   - If non-empty:
     5. `selected_item` (set to `search_results[0]`)
     6. `outfit_suggestion` (populated by `suggest_outfit`)
     7. `fit_card` (populated by `create_fit_card`)

---

## Sample Run

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Graphic Tee — 2003 Tour Bootleg Style — $24.0 on depop

  Outfit:   Hey there! FitFindr here, your go-to guide for making thrifted gems work hard in your rotation. 

That 2003 tour bootleg tee is an absolute score. The faded graphic and slightly boxy, worn-in cotton give it instant authenticity and effortless cool-guy/cool-girl energy. Since it leans heavily into grunge and streetwear, it’s super versatile. 

Here are two specific outfit pairings using pieces straight from your current wardrobe to style this piece:

Look 1: The Off-Duty Grunge Staple
- Top: Graphic Tee — 2003 Tour Bootleg Style
- Bottoms: Baggy straight-leg jeans, dark wash
- Shoes: Black combat boots
- Outerwear: Vintage black denim jacket

Why it works: The boxy fit of the tee pairs naturally with the volume of your baggy dark wash jeans for that authentic skate/grunge silhouette. Anchoring the bottom half with black combat boots creates a grounded look, while the vintage black denim jacket adds subtle texture play.

Look 2: High-Low Streetwear Contrast
- Top: Graphic Tee — 2003 Tour Bootleg Style
- Bottoms: Wide-leg khaki trousers
- Shoes: Chunky white sneakers
- Accessories: Brown leather belt

Why it works: Taking a grungy rock tee and pairing it with tailored, wide-leg khaki trousers gives you great contrast. Tucking the tee loosely and breaking the waistline with a leather belt creates an effortless, editorial streetwear fit.

  Fit card: Okay but can we talk about this find?? 😭🔥 

Just scored this 2003 tour bootleg tee on Depop for $24 and I am officially obsessed. The fade on the graphic? Immaculate. The boxy, perfectly worn-in cotton? Instant cool-girl/cool-guy energy without even trying. 

Y'all know I had to immediately test-drive it with pieces already sitting in the closet. Here’s how we’re styling it:

🖤 Look 1 (Off-Duty Grunge): Paired it with my favorite baggy straight-leg jeans, black combat boots, and tossed a vintage black denim jacket over top. The proportions are giving major early-2000s skate vibes, and the textures just work. 

✨ Look 2 (High-Low Streetwear): Tucked it loosely into some tailored wide-leg khaki trousers with a brown leather belt and chunky white sneakers. Mixing the grungy, beat-up tee with tailored pants creates that effortless "I just threw this on but look like a fashion week street style photographer took my picture" tension. 

Honestly? 10/10, absolute no-brainer. Drop a 💀 in the comments if you would've snatched this up too! 

#FitFindr #DepopFinds #ThriftHaul #StreetwearStyle #GrungeAesthetic #ThriftedFashion #OutfitInspo

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Hey there! I'm FitFindr, your go-to thrift stylist. Finding a solid pair of vintage Levi's 501s in a great medium wash is like hitting the thrift store jackpot—that natural knee fading gives them instant character. Here are two outfit pairings using pieces from your existing wardrobe:

Look 1: Off-Duty Streetwear
- White ribbed tank top
- Vintage black denim jacket
- Chunky white sneakers
- Black crossbody bag
Why it works: Tucking the white ribbed tank into high-waisted 501s creates a clean silhouette that balances the relaxed denim, while the black denim jacket adds contrast.

Look 2: Cozy-Chic Contrast
- Oversized grey crewneck sweatshirt
- Black combat boots
- Brown leather belt
Why it works: A slight front tuck of the oversized sweatshirt into the 501s defines the waist while keeping that lived-in feel, anchored by black combat boots.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers with black jacket', load_listings()[0]))"
Still pinching myself over this find 🥹✨ Scored these vintage Levi’s 501s in the perfect medium wash on Depop for literally $38. Keeping it stupid simple for the fit today: classic white sneakers, my go-to black jacket, and letting the denim do all the talking. Proof that the best pieces are the ones already in circulation. 🤌👖 #thrifting #depopfinds #levis501 #streetstyle
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked AI to propose acceptance criteria for our fit card tool that would be strictly measurable and testable.
- *What came back:* It returned a compound criterion checking four rules at once: word count between 20-55 words, dollar price inclusion, platform name, and at least two hashtags.
- *What I changed:* I simplified it down to a single-factor criterion focusing strictly on length (under 50 words). A compound criterion makes diagnosis ambiguous because when a test fails, you cannot cleanly isolate which requirement broke the run.

**Moment 2**

- *What I asked for:* I asked AI to help draft prompt templates in `tools.py` for `create_fit_card` and `suggest_outfit`.
- *What came back:* The suggested prompts included rigid guardrails like "strictly under 40 words" and "You MUST explicitly reference wardrobe items by exact name."
- *What I changed:* I removed those defensive constraints and used natural baseline prompts instead. This made the prompts more natural and did not overfit all the prompts just to try to pass our criteria.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
