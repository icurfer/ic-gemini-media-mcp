# Gemini media MCP

Local [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) tools for
Gemini Veo video generation. The server uses standard input/output and returns
an operation name immediately, so a client can poll and download later.

## Setup

```bash
uv sync
cp .env.example .env
chmod 600 .env
```

Put a Gemini key in the ignored `.env` file as `GEMINI_API_KEY=...`. Do not put
the key in MCP configuration, command arguments, source files, or chat messages.
The server also accepts `GEMINI_API_KEY` from its process environment.

Register in Codex:

```bash
codex mcp add ic-gemini-media -- /absolute/path/to/ic-gemini-media-mcp/.venv/bin/ic-gemini-media-mcp
```

Restart the MCP client after registration. The server reads `.env` using its own
repository path, regardless of the caller's working directory.

## Tools

| Tool | Purpose |
| --- | --- |
| `key_status` | Check whether a key is configured, without exposing it |
| `start_video` | Start a paid Veo 3.1 video job and return `operation_name` |
| `check_video` | Check a job from its operation name, including after restart |
| `download_video` | Download a completed job to a local `.mp4` file |

`start_video` accepts text only, one starting image, a first and last frame,
or up to three character reference images. Reference images cannot be combined
with first/last frames and require an 8-second video. The default is Veo 3.1
Fast, 8 seconds, 720p, portrait. Each call to `start_video` can incur a charge;
status and download calls do not generate a new video. See [Google's current
Veo guide](https://ai.google.dev/gemini-api/docs/veo) and
[pricing](https://ai.google.dev/gemini-api/docs/pricing) before generating.

No media is tracked in Git by default: downloaded files under `output/` are
ignored. For game assets, download to the game's source workspace instead.

## Verify

```bash
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q src
```

The tests use a fake video client and never spend API credit.
