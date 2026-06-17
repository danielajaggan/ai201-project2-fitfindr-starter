tool inventory

search_listings(description, size, max_price)
- Searches the mock listings dataset for items matching a text description, an optional size, and an optional maximum price.

inputs: 
description(str):"vintage graphic tee"
size` (str): size to filter by, e.g. "M" — 
max_price (float): highest acceptable price

outputs:
 A list of listing dictionaries, each containing id, title, description, category, style_tags, size, condition, price, colors, brand, and platform. Sorted by keyword-match relevance, best match first. Returns an empty list if nothing matches.

suggest_outfit(new_item, wardrobe)
**Purpose:** Given a listing the user is considering and their existing wardrobe, suggests how to style the new item using pieces they already own.

Inputs:
- new_item (dict): a listing dictionary, as returned by search_listings
- wardrobe (dict): the user's wardrobe, with an items key containing a list of wardrobe item dictionaries (id, name, category, colors, style_tags, notes)

Output: A string describing 1-2 suggested outfits, naming specific wardrobe pieces by name when available. If the wardrobe is empty, returns general styling advice instead.

create_fit_card(outfit, new_item)
Purpose: Formats the outfit suggestion and listing details into a short, casual, shareable caption (like an Instagram/TikTok OOTD post).

Inputs:
- outfit (str): the outfit suggestion string returned by suggest_outfit
- new_item (dict): the listing dictionary for the item being suggested

Output: A 2-4 sentence string mentioning the item name, price, and platform naturally, written in a casual, authentic tone. Returns a clear error message string instead of crashing if outfit is empty.

Planning Loop

The agent moves through its three tools in a fixed order, but checks results at each step before continuing. It starts by calling search_listings with the user's parsed description, size, and max price; if that returns an empty list, the agent stops immediately, sets an error message, and returns without calling the other two tools. If results are found, it selects the first one and passes it to suggest_outfit along with the user's wardrobe. If the wardrobe has no items that share a category, color, or style tag with the new item, the agent still continues — the suggestion simply notes that nothing complementary was found and recommends wearing the item on its own. Finally, the agent passes the outfit suggestion and the selected item to create_fit_card, which formats everything into the final response. The agent considers itself finished once create_fit_card produces an output, with the single early-exit point being the empty-search-results case.

State Management

The agent uses a session dictionary to store the original query, the parsed search parameters, the search results, the selected item, the outfit suggestion, the fit card, and any error — all in one place for the duration of a single interaction. Each tool only reads the specific piece of state it needs: suggest_outfit reads selected_item and wardrobe, while create_fit_card reads outfit_suggestion and selected_item. This means each tool's output is computed once and reused by the next step, rather than being recomputed or re-requested from the user.

---

Error Handling
| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Returns an empty list. The agent sets session[error] to "No listings found matching your search. Try a different size, a higher price range, or different keywords." and returns immediately without calling suggest_outfit or create_fit_card. Tested with the query "designer ballgown size XXS under $5" — confirmed this exact message was returned and no further tools were called. |
| suggest_outfit | Wardrobe is empty | The tool still calls the LLM, but with a prompt asking for general styling advice instead of wardrobe-specific pairings. Returns a non-empty string with general suggestions rather than crashing. |
| create_fit_card | Outfit input is missing or incomplete | If outfit is empty or whitespace-only, the tool returns "Unable to generate a fit card: no outfit suggestion was provided." without calling the LLM. |

AI Usage
Instance 1 — Tool implementations: I gave Claude the Tool 1, Tool 2, and Tool 3 spec blocks from my planning.md (inputs, return value, failure mode) one at a time, along with the existing docstrings and TODO steps already written in tools.py, and asked it to implement each function to match. Before trusting the generated code, I wrote small test scripts to specifically check each tool's failure mode — empty search results for search_listings, an empty wardrobe for suggest_outfit, and an empty outfit string for create_fit_card — and confirmed each one returned an informative message instead of crashing.

Instance 2 — Planning loop implementation: I gave Claude my planning.md's Planning Loop and State Management sections, along with the numbered TODO steps already in agent.py's run_agent() function, and asked it to implement the function to match. I verified the output by running the built-in CLI test cases at the bottom of agent.py — one happy-path query and one deliberate no-results query — and confirmed that suggest_outfit and create_fit_card were never called when search_listings returned an empty list, which matched the conditional logic I had specified in planning.md.