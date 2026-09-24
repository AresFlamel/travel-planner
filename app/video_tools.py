import base64
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


def generate_destination_video(
    prompt: str,
    tool_context: ToolContext = None,
) -> str:
    """Generates a short travel video or scenic destination preview using Gemini Omni (gemini-omni-flash-preview) in the global region, saves it as an artifact, uploads it to Cloud Storage, and returns the public video URL.

    Args:
        prompt: Detailed description of the travel video to generate (e.g. 'A 3-second scenic drone shot of tropical beaches in Cancun with palm trees').
        tool_context: ADK tool context injected automatically.

    Returns:
        A JSON string containing the prompt, filename, and public https URL of the generated video.
    """
    try:
        client = genai.Client(
            vertexai=True, project=FIRESTORE_PROJECT, location="global"
        )
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
            generation_config={"response_modalities": ["VIDEO"]},
        )

        video_bytes = None
        mime_type = "video/mp4"

        # 1. Check interaction.output_video
        if hasattr(interaction, "output_video") and interaction.output_video:
            ov = interaction.output_video
            idata = getattr(ov, "inline_data", None)
            if idata:
                d = idata.get("data") if isinstance(idata, dict) else getattr(idata, "data", None)
                m = (idata.get("mime_type") if isinstance(idata, dict) else getattr(idata, "mime_type", None)) or "video/mp4"
                if d:
                    video_bytes = base64.b64decode(d) if isinstance(d, str) else d
                    mime_type = m

        # 2. Check interaction.steps -> ModelOutputStep.outputs
        if not video_bytes and hasattr(interaction, "steps") and interaction.steps:
            for step in interaction.steps:
                outputs = getattr(step, "outputs", None)
                if not outputs and isinstance(step, dict):
                    outputs = step.get("outputs")
                if outputs:
                    for out in outputs:
                        d = out.get("data") if isinstance(out, dict) else getattr(out, "data", None)
                        m = (out.get("mime_type") if isinstance(out, dict) else getattr(out, "mime_type", None)) or "video/mp4"
                        if d:
                            video_bytes = base64.b64decode(d) if isinstance(d, str) else d
                            mime_type = m
                            break
                if video_bytes:
                    break

        if not video_bytes:
            return "Error: Model did not return any video bytes."

        filename = f"video_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp4"

        # 1. Save artifact with tool_context so it appears in Playground Artifacts panel
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(
                data=video_bytes, mime_type=mime_type
            )
            tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload video bytes directly to public Cloud Storage bucket (without writing to local file)
        storage_client = storage.Client(project=FIRESTORE_PROJECT)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = (
            f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
        )

        return json.dumps(
            {
                "prompt": prompt,
                "filename": filename,
                "public_url": public_url,
                "status": "Video successfully generated, saved as artifact, and uploaded to Cloud Storage.",
            },
            indent=2,
        )

    except Exception as e:
        return f"Error generating or uploading destination video: {str(e)}"
