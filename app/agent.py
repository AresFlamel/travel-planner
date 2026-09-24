# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from pathlib import Path

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback


from app.firestore_tools import (
    add_destination,
    get_destination_details,
    search_destinations,
)
from app.image_tools import generate_destination_postcard
from app.video_tools import generate_destination_video
from app.maps_tools import (
    find_nearby_places,
    geocode_address,
)


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


import json
import os
import urllib.request


def convert_currency(
    amount: float,
    from_currency: str = "USD",
    to_currency: str = "EUR",
) -> str:
    """Converts a monetary amount between currencies using real-time exchange rates from a public API.

    Args:
        amount: The monetary amount to convert (e.g. 100.0).
        from_currency: 3-letter source currency code (e.g., 'USD', 'EUR', 'GBP').
        to_currency: 3-letter target currency code (e.g., 'JPY', 'EUR', 'CAD').

    Returns:
        A JSON string containing the original amount, converted amount, exchange rate, and date.
    """
    from_curr = from_currency.upper().strip()
    to_curr = to_currency.upper().strip()

    if from_curr == to_curr:
        return json.dumps(
            {
                "amount": amount,
                "from_currency": from_curr,
                "to_currency": to_curr,
                "converted_amount": amount,
                "exchange_rate": 1.0,
                "date": "latest",
            },
            indent=2,
        )

    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if api_key:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_curr}/{to_curr}/{amount}"
    else:
        url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_curr}&to={to_curr}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

            if api_key:
                converted = data.get("conversion_result", amount)
                rate = data.get("conversion_rate", 1.0)
            else:
                rates = data.get("rates", {})
                converted = rates.get(to_curr, amount)
                rate = round(converted / max(0.0001, amount), 4)

            return json.dumps(
                {
                    "amount": amount,
                    "from_currency": from_curr,
                    "to_currency": to_curr,
                    "converted_amount": converted,
                    "exchange_rate": rate,
                    "date": data.get("date", "latest"),
                },
                indent=2,
            )
    except Exception as e:
        return f"Error fetching exchange rate from API: {str(e)}"


def calculate_trip_budget(
    num_days: int,
    num_travelers: int = 1,
    avg_lodging_per_night: float = 0.0,
    daily_food_budget: float = 0.0,
    daily_activities_budget: float = 0.0,
    transportation_per_person: float = 0.0,
    currency: str = "USD",
) -> str:
    """Calculates an itemized trip budget breakdown and per-person cost.

    Args:
        num_days: Duration of the trip in days (or nights).
        num_travelers: Number of people traveling together.
        avg_lodging_per_night: Estimated lodging cost per night.
        daily_food_budget: Estimated daily food expense per person.
        daily_activities_budget: Estimated daily activities expense per person.
        transportation_per_person: Transportation (flights/trains) cost per person.
        currency: Currency symbol or code (e.g. 'USD', 'EUR').

    Returns:
        A JSON string with total lodging, food, activities, transportation, total budget, and cost per person.
    """
    total_lodging = num_days * avg_lodging_per_night
    total_food = num_days * daily_food_budget * num_travelers
    total_activities = num_days * daily_activities_budget * num_travelers
    total_transportation = transportation_per_person * num_travelers

    grand_total = total_lodging + total_food + total_activities + total_transportation
    cost_per_person = grand_total / max(1, num_travelers)

    summary = {
        "num_days": num_days,
        "num_travelers": num_travelers,
        "currency": currency,
        "itemized_breakdown": {
            "lodging_total": round(total_lodging, 2),
            "food_total": round(total_food, 2),
            "activities_total": round(total_activities, 2),
            "transportation_total": round(total_transportation, 2),
        },
        "grand_total": round(grand_total, 2),
        "cost_per_person": round(cost_per_person, 2),
    }

    return json.dumps(summary, indent=2)


# Load code executor using deployment_metadata.json if available
metadata_file = Path(__file__).resolve().parent.parent / "deployment_metadata.json"
code_executor = None

if metadata_file.exists():
    try:
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        sandbox_resource_name = metadata.get("sandbox_resource_name")
        agent_engine_resource_name = metadata.get("remote_agent_runtime_id")

        if sandbox_resource_name:
            code_executor = AgentEngineSandboxCodeExecutor(
                sandbox_resource_name=sandbox_resource_name
            )
        elif agent_engine_resource_name:
            code_executor = AgentEngineSandboxCodeExecutor(
                agent_engine_resource_name=agent_engine_resource_name
            )
    except Exception as e:
        print(f"Warning: Failed to load deployment_metadata.json for code executor: {e}")


async def generate_memories_callback(callback_context: CallbackContext):
    """Sends session events to Memory Bank after each agent turn."""
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a Travel Planner AI agent. You assist users with discovering destinations, "
        "searching catalog destinations by budget/category, viewing destination details, "
        "adding new destinations, checking weather, calculating trip budgets, converting currency, "
        "geocoding addresses into coordinates, finding nearby attractions and hotels, "
        "generating destination postcard images, executing Python code safely in a sandbox, "
        "and planning travel itineraries."
    ),
    workflow_description="Analyze the user request and return structured UI cards when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects.\n\n"
        "MEMORY & TRAVEL PLANS:\n"
        "- Always remember and recall the user's travel plans, trip itineraries, preferred travel dates, "
        "destinations, budgets, dietary preferences, and travel companions across sessions.\n"
        "- Whenever a user shares details about a travel plan or asks to save/plan a trip, acknowledge "
        "that you have stored their travel plan in memory and reference their saved travel plans in future conversations."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        get_weather,
        get_current_time,
        search_destinations,
        get_destination_details,
        add_destination,
        calculate_trip_budget,
        convert_currency,
        geocode_address,
        find_nearby_places,
        generate_destination_postcard,
        generate_destination_video,
        PreloadMemoryTool(),
    ],
    code_executor=code_executor,
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
