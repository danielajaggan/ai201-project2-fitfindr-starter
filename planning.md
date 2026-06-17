# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
this tool searched the data containing listings abd returns a list that matches the description, size and price

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): ...Vintage Levi's 501 Jeans
- `size` (str): ...s
- `max_price` (float): ...38.00

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->a dictionary containing data from the schema such as id, title, description elc

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
if it fails then an error message is set
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
this take a new list from search listings and the users existing wardrobe the suggests how to style the new item using pieces the user already owns

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): ...id, title, category, style_tags, color
- `wardrobe` (dict): ...id, name, category, color, etc

**What it returns:**
<!-- Describe the return value --> 
returns a string with suggested outfits 

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? --> if it fails the tool returns a message stating that no pieces were found and suggest that the users weaes the new items on its own or consider other pieces

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences --> this takes original listing and suggested texts and summarizes them into an outfit

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (...): ...suggested outfit based in the suggest_outift

**What it returns:**
<!-- Describe the return value -->
a string with title, price,etc

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? --> the tool returns a messages telling the user that a fit could not be generated

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
the agent moves through the 3 tools in a fixed order but checks results at each step before continuing, it starts by calling search_listings with the user description, size and price, if that returns an empty string the agent stops and shows an error message instead of continuing.If results are found, it picks the first one and passes it to suggeted_fit along with the user's wardrobe. If the wardrobe has no items that share a category, color, or style tag with the new item, the agent still continues, but the suggestion simply notes that nothing complementary was found and recommends wearing the item on its own. Finally, the agent passes the outfit suggestion and the selected item to create_fit_card, which formats everything into a final response; if any required field is missing at this stage, it returns a partial result rather than failing outright. The agent considers itself finished once create_fit_card produces an output, with the single early-exit point being the empty-search-results case. 
---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

The agent stores information from the user's earlier messages and tool results in a session state, so it can refer back to them later instead of asking the user to repeat themselves. 
---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Returns an empty list. The agent sets session["error"] to a message like "No listings found matching your search. Try a different size, a higher price range, or different keywords." and returns immediately without calling suggest_outfit or create_fit_card. Tested with query "designer ballgown size XXS under $5" — confirmed this exact error message was returned. |
| suggest_outfit | Wardrobe is empty | The tool still calls the LLM, but with a prompt asking for general styling advice instead of wardrobe-specific pairings. It returns a non-empty string with general suggestions rather than crashing or returning an empty string.|
| create_fit_card | Outfit input is missing or incomplete |  If outfit is empty or whitespace-only, the tool returns the string "Unable to generate a fit card: no outfit suggestion was provided." without calling the LLM at all.|

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->
     
                                                                   

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

     I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement search_listings to filter by description, size and max_price.  I'll verify by checking that it handles the empty-results case and testing it with at least 3 different search queries.

     I'll give Claude my Tool 2 spec along with wardrobe schema and ask it to implement suggest_outfit to match the next items by categpry , color, styletag. I'll verify by testing with the example wardrobe and confirming the output references actual wardrobe items, not generic suggestions.

     I'll give Claude my Tool 3 spec and ask it to implement create_fit_card, combining the outfit suggestion and listing details into a formatted string. I'll verify by checking the output includes the item title, price, platform, and styling suggestion, and that it handles missing fields


**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
first the agent will access the database with the clothes and their cost, search_listings

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
then the get_example_wardrobe() is called to get the user example wardrobe to get this list of items in their closet

**Step 3:**
<!-- Continue until the full interaction is complete -->
finally the agent returns to the user a list of items that would be suitable from the two functions listed in step 1 and 2

**Final output to user:**
<!-- What does the user actually see at the end? --> 
i have found a vintage graphic tee for $27 on deepop that would go well with the baggy jeans of your choice.
