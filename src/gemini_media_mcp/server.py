"""Local stdio MCP server for Gemini Veo video jobs.

The credential is loaded from the process environment or this repository's
ignored .env file. Tool results and exceptions never include its value.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from google import genai
from google.genai import types
from mcp.server.fastmcp import FastMCP


ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
MODELS = {
    "veo-3.1-fast-generate-preview",
    "veo-3.1-generate-preview",
    "veo-3.1-lite-generate-preview",
}
mcp = FastMCP("ic-gemini-media")


def _api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or dotenv_values(ENV_FILE).get("GEMINI_API_KEY")
    if not isinstance(key, str) or not key.strip():
        raise ValueError(f"Gemini key is missing. Set GEMINI_API_KEY in {ENV_FILE}.")
    return key.strip()


def _client() -> genai.Client:
    return genai.Client(api_key=_api_key())


def _image(path: str) -> types.Image:
    source = Path(path).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError(f"Image must be an existing PNG, JPEG, or WebP file: {source}")
    return types.Image.from_file(location=str(source))


def _operation(client: genai.Client, name: str) -> types.GenerateVideosOperation:
    if not name or not name.strip():
        raise ValueError("operation_name is required")
    return client.operations.get(types.GenerateVideosOperation(name=name.strip()))


def _summary(operation: types.GenerateVideosOperation) -> dict[str, Any]:
    response = operation.response or operation.result
    videos = response.generated_videos if response else None
    return {
        "operation_name": operation.name,
        "done": bool(operation.done),
        "failed": bool(operation.error),
        "video_count": len(videos or []),
        "download_ready": bool(operation.done and videos),
    }


@mcp.tool()
def key_status() -> dict[str, Any]:
    """Check whether a Gemini key is configured; never print or test the key."""
    try:
        _api_key()
    except ValueError:
        return {"configured": False, "env_file": str(ENV_FILE)}
    return {"configured": True, "env_file": str(ENV_FILE)}


@mcp.tool()
def start_video(
    prompt: str,
    image_path: str | None = None,
    last_frame_path: str | None = None,
    reference_image_paths: list[str] | None = None,
    model: str = "veo-3.1-fast-generate-preview",
    duration_seconds: int = 8,
    aspect_ratio: str = "9:16",
    resolution: str = "720p",
    negative_prompt: str | None = None,
) -> dict[str, Any]:
    """Start a paid Veo video job. Use one start image or up to 3 character references.

    Returns an operation_name for check_video and download_video. Reference
    images require an 8-second job and cannot be combined with a start image.
    """
    if not prompt.strip():
        raise ValueError("prompt is required")
    if model not in MODELS:
        raise ValueError(f"model must be one of: {', '.join(sorted(MODELS))}")
    if duration_seconds not in {4, 6, 8}:
        raise ValueError("duration_seconds must be 4, 6, or 8")
    if aspect_ratio not in {"9:16", "16:9"}:
        raise ValueError("aspect_ratio must be 9:16 or 16:9")
    if resolution not in {"720p", "1080p", "4k"}:
        raise ValueError("resolution must be 720p, 1080p, or 4k")
    if resolution != "720p" and duration_seconds != 8:
        raise ValueError("1080p and 4k require 8 seconds")
    if model.endswith("lite-generate-preview") and resolution == "4k":
        raise ValueError("Veo Lite does not support 4k")
    references = reference_image_paths or []
    if len(references) > 3:
        raise ValueError("At most 3 reference images are supported")
    if references and (image_path or last_frame_path):
        raise ValueError("Reference images cannot be combined with first or last frames")
    if references and model.endswith("lite-generate-preview"):
        raise ValueError("Veo Lite does not support reference images")
    if references and duration_seconds != 8:
        raise ValueError("Reference images require 8 seconds")
    if last_frame_path and not image_path:
        raise ValueError("last_frame_path requires image_path")

    config_args: dict[str, Any] = {
        "duration_seconds": duration_seconds,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "number_of_videos": 1,
    }
    if negative_prompt:
        config_args["negative_prompt"] = negative_prompt
    if last_frame_path:
        config_args["last_frame"] = _image(last_frame_path)
    if references:
        config_args["reference_images"] = [
            types.VideoGenerationReferenceImage(image=_image(path), reference_type="asset")
            for path in references
        ]
    source = types.GenerateVideosSource(prompt=prompt, image=_image(image_path) if image_path else None)
    client = _client()
    try:
        operation = client.models.generate_videos(
            model=model, source=source, config=types.GenerateVideosConfig(**config_args)
        )
        return _summary(operation)
    finally:
        client.close()


@mcp.tool()
def check_video(operation_name: str) -> dict[str, Any]:
    """Check a Veo job by operation_name, including after an MCP restart."""
    client = _client()
    try:
        return _summary(_operation(client, operation_name))
    finally:
        client.close()


@mcp.tool()
def download_video(operation_name: str, output_path: str, overwrite: bool = False) -> dict[str, Any]:
    """Download a completed Veo job to a local MP4 path."""
    target = Path(output_path).expanduser().resolve()
    if target.suffix.lower() != ".mp4":
        raise ValueError("output_path must end in .mp4")
    if target.exists() and not overwrite:
        raise FileExistsError(f"File exists; set overwrite=true to replace it: {target}")
    client = _client()
    try:
        operation = _operation(client, operation_name)
        response = operation.response or operation.result
        videos = response.generated_videos if response else None
        if not operation.done or not videos:
            return {**_summary(operation), "saved": False}
        payload = client.files.download(file=videos[0].video)
        target.parent.mkdir(parents=True, exist_ok=True)
        mode = "wb" if overwrite else "xb"
        with target.open(mode) as output:
            output.write(payload)
        return {**_summary(operation), "saved": True, "path": str(target), "bytes": len(payload)}
    finally:
        client.close()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
