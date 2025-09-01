Model Token Limits

Overview
- aifred uses best-effort defaults for model context windows and maximum output tokens to size requests when you don’t specify `@max`.
- These values are indicative and may change as providers update their models.
- You can override or extend the table via Alfred Settings (user config) or by providing a JSON file.

Built-in (indicative)
- OpenAI
  - gpt-4o, gpt-4o-mini, gpt-4-turbo, o4, o4-mini, o3-mini: context ≈ 128k, max output ≈ 4096
- Anthropic
  - claude-3-7-sonnet, claude-3-5-sonnet-20241022, claude-3-opus-20240229: context ≈ 200k, max output ≈ 8192
  - claude-3-5-haiku-20241022, claude-3-haiku-20240307: context ≈ 200k, max output ≈ 4096

Override via Alfred Settings
- `alfred_settings.py` persists settings in the Alfred data directory.
- You can add a `model_caps` object to the configuration file (aifred_config.json) and define entries like:

```
{
  "model_caps": {
    "openai:gpt-4o": {"context": 120000, "max_output_tokens": 4096},
    "anthropic:claude-3-7-sonnet": {"context": 200000, "max_output_tokens": 8192}
  }
}
```

Override via JSON file
- Set `AIFRED_MODEL_CAPS_PATH` to a JSON file with the same shape as above.
- File entries take precedence over built-in values.

Notes
- aifred computes input token budget as: `context_window − planned_output_tokens`.
- `@max:<n>` forces planned output tokens to `<n>`; otherwise aifred uses the model’s default max.
