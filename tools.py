import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


def _get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


def search_listings(description, size=None, max_price=None):
    listings = load_listings()

    if max_price is not None:
        listings = [item for item in listings if item["price"] <= max_price]

    if size is not None:
        listings = [
            item for item in listings
            if size.lower() in item["size"].lower()
        ]

    keywords = description.lower().split()
    scored = []
    for item in listings:
        searchable_text = " ".join([
            item["title"].lower(),
            item["description"].lower(),
            " ".join(item["style_tags"]).lower(),
        ])
        score = sum(1 for kw in keywords if kw in searchable_text)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [item for score, item in scored]


def suggest_outfit(new_item, wardrobe):
    client = _get_groq_client()
    items = wardrobe.get("items", [])

    if not items:
        prompt = (
            f"A user is considering buying this item:\n"
            f"Name: {new_item['title']}\n"
            f"Category: {new_item['category']}\n"
            f"Colors: {', '.join(new_item['colors'])}\n"
            f"Style tags: {', '.join(new_item['style_tags'])}\n\n"
            f"They don't have any wardrobe items on file yet. Give general "
            f"styling advice: what kinds of pieces would pair well with this "
            f"item, and what vibe or occasions does it suit?"
        )
    else:
        wardrobe_text = "\n".join(
            f"- {item['name']} (category: {item['category']}, "
            f"colors: {', '.join(item['colors'])}, "
            f"style: {', '.join(item['style_tags'])})"
            for item in items
        )
        prompt = (
            f"A user is considering buying this item:\n"
            f"Name: {new_item['title']}\n"
            f"Category: {new_item['category']}\n"
            f"Colors: {', '.join(new_item['colors'])}\n"
            f"Style tags: {', '.join(new_item['style_tags'])}\n\n"
            f"Their existing wardrobe:\n{wardrobe_text}\n\n"
            f"Suggest 1-2 complete outfits that pair this new item with "
            f"specific pieces from their wardrobe by name."
        )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content


def create_fit_card(outfit, new_item):
    if not outfit or not outfit.strip():
        return "Unable to generate a fit card: no outfit suggestion was provided."

    client = _get_groq_client()
    prompt = (
        f"Write a short, casual Instagram/TikTok-style OOTD caption (2-4 sentences) "
        f"for this thrifted find:\n"
        f"Item: {new_item['title']}\n"
        f"Price: \\n"
        f"Platform: {new_item['platform']}\n\n"
        f"Outfit styling notes:\n{outfit}\n\n"
        f"Mention the item name, price, and platform naturally, once each. "
        f"Capture the outfit's vibe in specific terms. Sound authentic, not "
        f"like a product description."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )

    return response.choices[0].message.content
