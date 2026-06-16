from tools import suggest_outfit
from utils.data_loader import load_listings, get_example_wardrobe

item = load_listings()[0]
wardrobe = get_example_wardrobe()

result = suggest_outfit(item, wardrobe)
print("RESULT:", repr(result))
