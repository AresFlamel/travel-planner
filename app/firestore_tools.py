import json
from typing import Optional
from google.cloud import firestore

# Hardcode GCP project ID as a string per user requirements
FIRESTORE_PROJECT = "qwiklabs-gcp-03-6a88f0f41795"


def get_firestore_client() -> firestore.Client:
    """Initializes and returns a Firestore client configured for the project."""
    return firestore.Client(project=FIRESTORE_PROJECT)


def search_destinations(category: Optional[str] = None, max_budget_per_day: Optional[float] = None) -> str:
    """Searches travel destinations from the Firestore backend database based on category or daily budget.

    Args:
        category: Optional category filter (e.g. 'Culture', 'Modern', 'Food', 'Nature', 'Metropolis').
        max_budget_per_day: Optional maximum average cost per day in USD.

    Returns:
        A JSON formatted string listing the matching travel destinations and their key details.
    """
    db = get_firestore_client()
    docs = db.collection("destinations").stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        
        # Filter by category if provided
        if category and category.lower() not in data.get("category", "").lower():
            continue
            
        # Filter by max budget per day if provided
        if max_budget_per_day is not None and data.get("avg_cost_per_day", 0.0) > max_budget_per_day:
            continue
            
        results.append(data)
        
    if not results:
        return "No travel destinations found matching your specified criteria."
        
    return json.dumps(results, indent=2)


def get_destination_details(destination_id: str) -> str:
    """Retrieves full details for a specific travel destination document from Firestore.

    Args:
        destination_id: The unique identifier for the destination (e.g., 'paris', 'tokyo', 'kyoto', 'new-york').

    Returns:
        A JSON string containing the detailed information for the destination, or an error message if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection("destinations").document(destination_id.lower().strip())
    doc = doc_ref.get()
    
    if not doc.exists:
        return f"Destination ID '{destination_id}' not found in the travel database."
        
    return json.dumps(doc.to_dict(), indent=2)


def add_destination(
    destination_id: str,
    name: str,
    country: str,
    category: str,
    description: str,
    avg_cost_per_day: float,
    best_season: str,
    highlights: Optional[str] = None,
) -> str:
    """Adds or updates a travel destination entry in the Firestore database.

    Args:
        destination_id: A unique lowercase identifier (e.g., 'rome', 'barcelona').
        name: Name of the destination city or place.
        country: Country where the destination is located.
        category: Category of travel (e.g., 'History & Art', 'Beach & Resort').
        description: Summary description of the destination.
        avg_cost_per_day: Estimated average daily cost per person in USD.
        best_season: Best time of year to visit.
        highlights: Comma-separated list of top attractions or highlights.

    Returns:
        A confirmation message indicating successful write to Firestore.
    """
    db = get_firestore_client()
    clean_id = destination_id.lower().strip().replace(" ", "-")
    
    highlights_list = [h.strip() for h in highlights.split(",")] if highlights else []
    
    data = {
        "id": clean_id,
        "name": name,
        "country": country,
        "category": category,
        "description": description,
        "avg_cost_per_day": float(avg_cost_per_day),
        "best_season": best_season,
        "highlights": highlights_list,
    }
    
    db.collection("destinations").document(clean_id).set(data)
    return f"Successfully saved destination '{name}' (ID: {clean_id}) to Firestore."
