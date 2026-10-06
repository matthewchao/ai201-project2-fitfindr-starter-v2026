# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
Our query parser and search use plain keyword matching, regex extraction, and external model calls. Some natural phrasing variations or transient model network delays may occasionally fail to produce an end-to-end completion, making 4 of 5 a realistic standard for a non-deterministic pipeline while 5 of 5 would ignore natural query ambiguity.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
Unlike the happy path, branching on an empty search result is pure deterministic control flow (`if not results: return session`). There are no model calls or external network dependencies in this decision path, so once an empty list is returned, the loop must halt 100% of the time (5 of 5 tries) without exception.

---

## 3. Session state integrity across tool calls

Given a query that matches at least one listing, `session["selected_item"]` holds the exact item dictionary returned in `session["search_results"][0]` (matching `id`, `title`, and `price`), and that exact item dictionary is passed into `suggest_outfit` and `create_fit_card` without key mutations or data loss — in 5 of 5 tries.

**Why this target:**
State management in our planning loop is pure deterministic Python dictionary access. Unlike generative model responses or external network APIs, reading from and writing to `session` has no stochastic variation or external failure modes. Any failure to preserve the selected item between tools would be a fundamental logic defect in the agent loop rather than acceptable variance, so 5 of 5 is the appropriate standard.

---

## 4. Fit card brevity for social sharing

Across 5 test runs on distinct items, the caption returned by `create_fit_card` is concise and social-media ready, containing strictly fewer than 50 words — in 5 of 5 tries.

**Why this target:**
A thrift fit card is meant to be a short, shareable social caption rather than a lengthy descriptive paragraph. Generative language models naturally drift toward wordy explanations unless constrained. We set an ambitious target of 5 of 5 with a 50-word ceiling to hold our prompt to a strict brevity standard, providing an unambiguous, measurable threshold to diagnose and tune if verbosity occurs.

---

## 5. Wardrobe inventory grounding in outfit recommendations

Given an item and a user wardrobe containing inventory pieces, `suggest_outfit` explicitly references at least one existing piece by its exact `name` from `wardrobe["items"]` in its recommendations — in 5 of 5 tries.

**Why this target:**
The core value proposition of FitFindr is connecting thrifting finds to clothes the user already owns. Recommending generic staples (like "white sneakers" or "dark jeans") that aren't in the user's wardrobe breaks user trust and defeats the purpose of maintaining a wardrobe state. We set a 5 of 5 target to enforce that our prompt strictly grounds the model's outfit recommendations in the user's actual inventory.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
