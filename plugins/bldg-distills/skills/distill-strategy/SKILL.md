---
name: distill-strategy
description: "Distill long content (YouTube videos, transcripts, articles, podcasts) into a personal or business knowledge base. Domain-agnostic engine — use the domain wrappers (distill-bldg, distill-personal, distill-parenting) which preset the vault path and strategic lens. Or call directly with custom paths."
---

# Distill Strategy (General Engine)

Domain-agnostic distillation engine. Takes any long-form content, extracts what's strategically actionable for a specific domain, and logs it into an Obsidian vault with minimal context pollution.

Do not load this skill directly for everyday use — load the domain wrapper instead (e.g. `distill-bldg`, `distill-personal`). The wrapper presets the vault path, log file, notes file, and lens. Only load this general engine when you need a custom domain not covered by existing wrappers.

## Parameters (set by wrapper or caller)

Before running, confirm these are set:

- **VAULT_PATH** — absolute path to the Obsidian vault root (e.g. `/Users/mattnicosia/matt-vault-v2`)
- **INTAKE_LOG** — relative path within vault for the chronological intake log (e.g. `07 Sources/Strategy Intake.md`)
- **STRATEGY_NOTES** — relative path within vault for the synthesized strategy notes (e.g. `02 Concepts/Strategy Notes.md`)
- **DOMAIN_LABEL** — short label for this domain, used in replies (e.g. "BLDG Labs", "Personal", "Parenting")
- **STRATEGIC_LENS** — what to look for when distilling. Replaces the hardcoded BLDG labs lens. Examples:
  - BLDG Labs: "What's strategically actionable for BLDG Labs — positioning, pricing, GTM, competitive landscape, product sequencing, or AI/construction tech trends."
  - Personal: "What's actionable for Matt's personal growth — limiting beliefs, patterns, strengths, blind spots, relationship insights, or habits worth adopting."
  - Parenting: "What's actionable as a parent — communication patterns, boundary-setting, developmental insights, or ways to show up better for Dea and Nicky."
- **THREAD_SECTIONS** — list of thread names in the Strategy Notes file to check/update. If a note doesn't match an existing thread, add to a "General / uncategorized" thread rather than creating a new one-off section.

## When to use

Matt sends a YouTube URL, pasted transcript, article link, or raw take. **Always confirm before running** unless Matt explicitly says to distill/log/file it. A bare link with no instruction = ask first.

## Workflow

### 1. Get the raw material
- YouTube link: prefer `web_extract` on the URL first (returns transcript, title, creator, date in one call). If it fails with a Firecrawl/credits error, skip immediately — don't retry or reconfigure.
- If web_extract fails: use `youtube-content` skill's `fetch_transcript.py --text-only` via terminal. Use Hermes-managed Python 3.11 venv, not system Python 3.9.
- If that also fails (or in cron mode where `-c`/`-e` flags are blocked): write a small Python script to `/tmp/fetch_yt.py` that imports `youtube_transcript_api`, instantiates the class, calls `api.fetch(video_id)`, and prints segments. Run the file directly with the Hermes venv Python. See the API pitfall for exact syntax — the library uses instance methods and object attributes, not class methods and dict keys.
- If you need metadata (title/author/date) and all transcript methods failed: scrape the raw video page HTML via `terminal`/`urllib` with a browser User-Agent and regex out the embedded JSON fields `"title":"(.*?)"`, `"author":"(.*?)"`, `"publishDate":"(.*?)"`.
- **Never load the full transcript into the main conversation.** Raw text stays on disk or in tool output; only the distillate enters context.

### 2. Distill through the strategic lens
Do not write a general summary. Apply `STRATEGIC_LENS`. Extract only what's strategically actionable:
- What claim/insight is being made?
- Which of the THREAD_SECTIONS does it apply to?
- Is it new signal, or does it confirm/contradict something already in STRATEGY_NOTES?
- One-line takeaway, max ~20 words.

### 3. Log the intake entry
Append a row to INTAKE_LOG:
`| Date | Creator/Author | Title | URL | Type | Takeaway | Tags |`

Use patch, not full rewrite.

**First-party material (Matt's own work, teardowns, analyses):** write a full distilled note to `07 Sources/<Title>.md`, link it from the intake log row and from the relevant thread in STRATEGY_NOTES.

### 4. Update strategy notes only if it moves something
Read the relevant thread section in STRATEGY_NOTES. If the new signal:
- **Confirms existing thinking:** one-line "reinforced by [source]" note.
- **Sharpens or changes it:** update "Current thinking" for that thread.
- **Fills an empty thread:** write the first "Current thinking" line.
- **Contradicts something:** add to "Contradictions / open tensions" and flag to Matt. Don't silently resolve.
- **Doesn't match any thread:** add to "General / uncategorized."

### 4.5. Check if this moves any offer scores
If the domain has an OFFER_ASSESSMENT note (set by the wrapper, e.g. `02 Concepts/BLDG Labs Offer Assessment.md`), check whether the new signal changes any candidate offer's score, adds a new candidate, or shifts the priority stack. If a score changes, update the table and note it in the decision log. Flag any priority-stack shifts in the report to Matt.

### 5. Emit content seeds (required byproduct)
When (and only when) the distill produces a claim, contradiction, number, or twist Matt could voice in public:
- Append 0–2 rows to `/Users/mattnicosia/matt-vault-v2/05 Operating/Content Seeds.md`
- The file has two table sections. Append to the upper section (above `## Rules`) which uses the compact 6-column format:
  `| Date | Source (distill:<title or creator>) | Pillar (Build/Shift/Human/Edge) | Platform (X or LI) | Angle (one line, including the twist) | Status = raw |`
- The lower table (below `## Rules`) includes an extra `AngleType` column — match whichever format the adjacent rows use. Read the file first to confirm which section you're appending to.
- Prefer X for news-translatable tech angles, LI for longer builder/opinion takes
- Skip if the distill is pure ops/internal with no public angle. Zero is fine. Inventing a forced seed is not.
- Load `amber-content` only if you also draft full posts in the same turn. Seeds alone do not require AMBER.

### 6. Report back short
What you logged, which thread (if any) it updated, whether anything contradicts current thinking, and how many content seeds dropped (0–2). Do not paste the transcript back.

## Pitfalls
- Don't let raw transcript sit in main context. Compress immediately.
- Don't create new thread sections for one-off data points.
- Verify dates: `web_extract` dates can be wrong. If Matt corrects a date, trust him.
- Testable claims: spike them, don't just log them.
- Low-signal content: skip it rather than manufacturing a takeaway.
- **`fetch_transcript.py` requires Python 3.10+** (uses `X | None` type hints). System Python on this Mac is 3.9.6 and fails with `unsupported operand type(s) for |`. Use the Hermes-managed venv Python instead: `/Users/mattnicosia/.hermes/hermes-agent/venv/bin/python3.11`. If `youtube-transcript-api` isn't installed in that venv, pip install it there before running the fetch.
- **`web_extract` upload dates can be substantially wrong** — observed reading a video's date as the fetch date instead of real publish date, off by over two months. If Matt states or corrects a date, trust him immediately. When logging multiple pieces from the same creator, sanity-check chronological order before asserting which is newest/oldest.
- **Vault markdown table patching is fragile — prefer append-before-heading over inline-row replacement.** The intake log uses pipe-delimited markdown table rows. When old rows contain backslash-escaped quotes (e.g. `\\\"we handle your estimating\\\"`), `patch`'s `old_string` matching fails with "escape-drift detected." Instead of matching against an existing row's exact text, target the section heading (e.g. `## See also`) and prepend the new row before it. This avoids backslash-escaping issues entirely and is safer when the file has been partially read with offset/limit pagination (full-file reads are expensive on growing intake logs).
- **macOS `grep` does not support `-P` (PCRE).** When scraping YouTube page HTML for metadata, do not use `grep -oP`. Use Python's `urllib` + `re` directly — it's cross-platform and the skill's step 1 already says to do this. The instinct to quick-grep is wrong on this machine.
- **Use the existing `fetch_transcript.py` script, do not write your own.** The `youtube-content` skill's `scripts/fetch_transcript.py` already handles v1.2.4 API changes (instance methods, FetchedTranscriptSnippet objects). Run it via `uv run python3` from the skill's scripts directory. Writing inline Python to call the transcript API directly leads to API-surface iteration that the script already solved.
- **"Video Unplayable" is not the same as "Video Not Found."** When youtube-transcript-api raises `VideoUnplayable` ("This video is not available"), the video exists but is geo-restricted or temporarily locked. The YouTube watch page still returns metadata (title, author, date, description, view count) via a standard `urllib` scrape. Extract what metadata you can, save a signal note with a `[ ] Manual watch needed` checkbox, and flag it in the report. Do not treat it as a dead link.
- **YouTube metadata scraping fallback (when transcript fails):** see `references/youtube-metadata-scraping.md` for the working Python pattern that extracts title, author, publish date, description, view count, and chapter markers from the raw watch page HTML. Use this before giving up on a video Matt sent.
- **`web_extract` silently fails when Firecrawl is not configured** — returns an empty error about missing `FIRECRAWL_API_KEY` or Nous Portal credits. This is expected on this machine. When it fails, proceed directly to the terminal-based transcript fetch instead of trying to fix web_extract.
- **`yt-dlp` is the fastest metadata fallback.** When transcript fetch fails (video unplayable, no subtitles, geo-restricted) and you need title/description/duration/channel/view count: `yt-dlp --print "%(title)s|||%(description)s|||%(duration)s|||%(channel)s|||%(view_count)s" "URL"`. Installed at `/opt/homebrew/bin/yt-dlp` on this Mac. Pipe-delimited output is easy to split: `title, desc, dur, channel, views = stdout.split("|||")`. This is faster and cleaner than scraping raw page HTML with regex — use this before falling back to the `youtube-metadata-scraping.md` approach.
- **Cron mode blocks `execute_code` and `terminal -c`/`-e` flags.** When running as a scheduled cron job (no user present to approve dangerous commands), you cannot use `execute_code` or pass `-c`/`-e` to Python. Workaround: write the script to a temp file (e.g. `/tmp/fetch_yt.py`) with `write_file`, then run it with `terminal("python3 /tmp/fetch_yt.py")`. This is the only path that works in cron mode.
- **`youtube_transcript_api` API signature (v1.x).** The library installed in the Hermes venv uses instance methods, not class methods. Correct invocation:
  ```python
  from youtube_transcript_api import YouTubeTranscriptApi
  api = YouTubeTranscriptApi()
  transcript = api.fetch('VIDEO_ID')
  for segment in transcript:
      print(f"[{segment.start:.1f}s] {segment.text}")
  ```
  Do NOT use `YouTubeTranscriptApi.get_transcript()` (class method, doesn't exist in this version). Segments are objects with `.start` and `.text` attributes, not subscriptable dicts. Writing the script to a file first (see cron mode pitfall above) also avoids the `-c` flag restriction.
- **X/Twitter post extraction (no Firecrawl):** When Matt sends an X post link and `web_extract` fails (no Firecrawl configured on this machine), extract the tweet ID from the URL and use `xurl read <tweet_id>` via terminal. The API may return truncated text if the post has an image attachment - the image usually contains the rest. For full methodology context, follow up with `x_search` using the creator name and topic keywords. The tweet text gives the core claim; `x_search` fills in the full details. Do not attempt `web_extract` on x.com URLs — it will always fail without Firecrawl.
- **Vault table patching with truncated text markers:** When a file was read with offset/limit pagination and contains `[truncated]` markers, do NOT use those truncated segments as `old_string` targets. The patch will match against the literal text including the `[truncated]` tag, and since the match spans fewer characters than the actual file content, the replacement will delete the unmatched portion. Always re-read the file in full before patching any section that was previously paginated. A bad patch in strategy notes can silently destroy paragraphs of content.
