# Degraded-Sources Research

When `web_search`, `web_extract`, `image_generate`, and `/last30days` are unavailable (Firecrawl billing / credits exhausted on Nous Portal), use these fallback techniques.

## Primary workaround: raw HTTP via terminal/execute_code

Raw `curl` in terminal or `urllib` in execute_code often works when Hermes-branded web tools don't. These tools use different network paths and auth:

```bash
# YouTube transcript (using existing skill scripts)
python3 /path/to/youtube-content/scripts/fetch_transcript.py "URL" --text-only

# DuckDuckGo lite (no JS, basic HTML)
curl -s --max-time 15 "https://lite.duckduckgo.com/lite/?q=SEARCH_TERMS" \
  -H "User-Agent: Mozilla/5.0"

# YouTube metadata
curl -s --max-time 10 "https://www.youtube.com/watch?v=VIDEO_ID" | \
  grep -o '"ownerChannelName":"[^"]*"'

# GitHub raw content (three.js examples, spec files)
curl -s --max-time 15 "https://raw.githubusercontent.com/OWNER/REPO/BRANCH/PATH"

# Market research pages (many block scrapers — try with User-Agent header)
curl -s --max-time 15 "URL" -H "User-Agent: Mozilla/5.0"
```

## Technique: execute_code with urllib

For multi-URL fetching with pattern matching:

```python
import urllib.request, re, json

urls = ["https://example1.com", "https://example2.com"]
for url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract what you need with regex or string search
        billions = re.findall(r'\$\s*\d+[\.\d]*\s*(?:billion|million|trillion)', html)
```

## Always note degraded status

When presenting KEYSTONE-7 runs, distillations, or any output that would normally benefit from live wave research:
- Label: `Sources: degraded (missing X, YouTube, /last30days, web_search, web_extract)`
- Resonance modifier is locked to Neutral for all concepts
- 85+ KEYSTONE-7 build band is essentially unreachable without real-world evidence already attached

## Known working endpoints

- `https://www.youtube.com/watch?v=ID` — page metadata (title, channel, publish date)
- `https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/FILENAME` — three.js examples
- `https://www.marketsandmarkets.com/Market-Reports/` — market research pages (some accessible)
- IBISWorld industry pages — roofing industry data accessible via raw HTTP
