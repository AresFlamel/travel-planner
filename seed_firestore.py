from google.cloud import firestore

# Hardcode project ID as a string per requirements to avoid project number issues on Agent Platform
FIRESTORE_PROJECT = "qwiklabs-gcp-03-6a88f0f41795"

def seed_destinations():
    db = firestore.Client(project=FIRESTORE_PROJECT)
    destinations_ref = db.collection("destinations")
    
    sample_destinations = [
        {
            "id": "paris",
            "name": "Paris",
            "country": "France",
            "category": "Culture & Art",
            "description": "City of Light known for the Eiffel Tower, Louvre Museum, and world-class cafes.",
            "highlights": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral"],
            "avg_cost_per_day": 180.0,
            "best_season": "Spring (April - June)",
        },
        {
            "id": "tokyo",
            "name": "Tokyo",
            "country": "Japan",
            "category": "Modern & Food",
            "description": "Bustling metropolis combining ultra-modern skyscrapers with historic temples.",
            "highlights": ["Shinjuku", "Senso-ji Temple", "Shibuya Crossing"],
            "avg_cost_per_day": 150.0,
            "best_season": "Autumn (October - November)",
        },
        {
            "id": "kyoto",
            "name": "Kyoto",
            "country": "Japan",
            "category": "Culture & Nature",
            "description": "Japan's ancient capital famed for classical Buddhist temples, gardens, and shrines.",
            "highlights": ["Fushimi Inari-taisha", "Arashiyama Bamboo Grove", "Kinkaku-ji"],
            "avg_cost_per_day": 130.0,
            "best_season": "Spring (March - April)",
        },
        {
            "id": "new-york",
            "name": "New York City",
            "country": "USA",
            "category": "Metropolis & Theater",
            "description": "The Big Apple featuring iconic landmarks, Broadway shows, and diverse neighborhoods.",
            "highlights": ["Central Park", "Statue of Liberty", "Broadway"],
            "avg_cost_per_day": 220.0,
            "best_season": "Autumn (September - November)",
        }
    ]

    for item in sample_destinations:
        destinations_ref.document(item["id"]).set(item)
        print(f"✅ Successfully seeded destination: {item['name']} ({item['id']})")

if __name__ == "__main__":
    seed_destinations()
