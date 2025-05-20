# OpenAI Dictation Integration

Caster includes optional modules for leveraging OpenAI services to transcribe and refine dictated text. The two modules are:

- `castervoice.lib.openai_utils` – wraps the `openai` Python package and exposes helper methods for Whisper transcription and GPT based text refinement.
- `castervoice.lib.openai_recorder` – records audio from the microphone, uses `openai_utils` to process it and pastes the results back into the active application.

## Configuration

1. Install the `openai` Python package (already included in `requirements.txt`).
2. Provide your OpenAI API key via the `OPENAI_API_KEY` environment variable so that `OpenAIUtils` can authenticate.
3. Load the `openai_dictation_rules` rule and issue the voice command `dictate` to start recording. Use `append`, `edit` and `dictate off` to control processing.

## Privacy considerations

When this feature is enabled, captured audio and text are sent to OpenAI servers for transcription and language‑model processing. This may include sensitive information. Review OpenAI's terms and privacy policy before using the feature and disable it if you are uncomfortable sending data to third‑party services.

This functionality is experimental and disabled by default. Only enable it if you have configured an API key and understand the privacy implications.
