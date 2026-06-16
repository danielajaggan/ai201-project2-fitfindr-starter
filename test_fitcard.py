from tools import suggest_outfit, create_fit_card
from utils.data_loader import load_listings, get_example_wardrobe

item = load_listings()[0]
wardrobe = get_example_wardrobe()

outfit = suggest_outfit(item, wardrobe)
print("OUTFIT:", outfit)
print()

card = create_fit_card(outfit, item)
print("FIT CARD:", card)
