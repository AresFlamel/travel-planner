import json
import time
import uuid
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

# Hardcode GCP project and Cloud Storage bucket as strings per requirements
FIRESTORE_PROJECT = "qwiklabs-gcp-03-6a88f0f41795"
GCS_BUCKET_NAME = "travel-planner-media-6a88f0f4"


def generate_destination_postcard(
    prompt: str,
    tool_context: ToolContext = None,
) -> str:
    """Generates a high-quality travel postcard or spot preview image for a destination, saves it as an artifact, uploads it to Cloud Storage, and returns the public image URL.

    Args:
        prompt: Detailed description of the travel postcard or destination image to generate (e.g. 'A scenic sunset view of the Eiffel Tower in Paris').
        tool_context: ADK tool context injected automatically.

    Returns:
        A JSON string containing the prompt, filename, and public https URL of the generated image.
    """
    try:
        # 1. Generate image using gemini-3.1-flash-lite-image in global region
        client = genai.Client(vertexai=True, project=FIRESTORE_PROJECT, location="global")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            ),
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return "Error: Model did not return any image data."

        filename = f"postcard_{int(time.time())}_{uuid.uuid4().hex[:6]}.jpg"

        # 2. Save with tool_context.save_artifact so it shows up in Playground's Artifacts panel
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 3. Upload same image bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"

        return json.dumps(
            {
                "prompt": prompt,
                "filename": filename,
                "public_url": public_url,
                "status": "Image successfully generated, saved as artifact, and uploaded to Cloud Storage.",
            },
            indent=2,
        )

    except Exception as e:
        return f"Error generating or uploading destination postcard: {str(e)}"
