# AI Authoring Guide (Kamal‑style)

Guidelines for AI agents writing registry docs to match the Kamal aesthetic: text‑first, fast to scan, minimal chrome.

## Tone and Layout
- Use a single, narrow column; keep paragraphs short.
- Lead with what matters: task purpose, how to run it, and required parameters.
- Avoid heavy branding, hero banners, or busy nav. One level of headings is enough.
- Prefer sentences over lists unless bullets improve scanning.
- Keep code blocks concise and runnable.

## Formatting Rules
- Headings: Sentence case, brief (`## Usage`, `## Parameters`).
- Links: inline markdown, no buttons.
- Code: fenced blocks with a language tag; avoid inline pseudo‑code.
- Tables: only if they simplify comparison; otherwise stick to bullets.
- Whitespace: add blank lines between sections; avoid dense multi-level lists.

## Example (Epoch Settings)
Minimal snippet showing the new event‑stripping options:

```python
"epoch_settings": {
    "enabled": True,
    "value": {"tmin": -0.5, "tmax": 1.0},
    # Only time-lock to stimulus/target; keep BAD_* for rejection
    "event_id": {"13": 1, "14": 2},
    "strip_other_events": True,
    "allowed_events": ["13", "14"],
    "remove_baseline": {"enabled": False, "window": [-0.2, 0.0]},
    "threshold_rejection": {
        "enabled": False,
        "volt_threshold": {"eeg": 0.000125},
    },
    # Add other epoch tuning here if needed (e.g., keep_all_epochs)
},
```

Keep snippets tight: no extra comments beyond what helps a reader act. Render the page as plain markdown suitable for GitHub Pages.***
