---
name: add-to-estimating-bldg
description: Creates a new project folder in the BLDG Estimating Dropbox directory by duplicating the master template folder and naming it with the next sequential job number, following Matt's "NNNNNN - Property/Client [Tag]" convention. Use whenever Matt asks to set up, create, or start a new estimate/job/project folder for BLDG Estimating — phrases like "set up a new estimate folder", "create a job folder for [property]", "start a new BLDG project for [client]", "make a new estimating folder", "what's the next job number", or when he just gives a property address or client name plus a tag (e.g. "[Violante]", "[O+D]") and wants a folder for it.
---

# New BLDG Estimating job folder

## What this does

Duplicates the master template folder (`Estimate Folder Template [COPY & PASTE ONLY]`) inside `/BLDG/BLDG Estimating` on Dropbox, and renames the copy to follow Matt's naming convention:

`{job number} - {property or client name} [{tag}]`

Job numbers are 6-digit and sequential across all of BLDG Estimating — not per year, and not gapless in any predictable way (job 260106 sits right next to much older jobs like 260001). The bracketed tag at the end is usually an estimator's surname or a GC/client shorthand (Violante, Tener, GTL, O+D, M&M, etc.). It's optional — some existing folders skip it entirely, e.g. `260080 - 317 Manhattan Avenue`.

Do this through the Dropbox MCP connector directly (`mcp__Dropbox__*` tools). There's no need to touch Finder, request local folder access, or drive any app's UI — the connector already reaches these exact files.

## Steps

1. **Get the property/client name and tag.** If the request doesn't already include both, ask:
   - The property, client, or project name — becomes the middle of the folder name.
   - The bracketed tag, if any (estimator name, GC, or client code). It's fine if there isn't one — don't invent one.

2. **Find the next job number.** List the *direct, top-level* children of `/BLDG/BLDG Estimating` with `mcp__Dropbox__list_folder` (`recursive: false`, `object_types: ["folder"]`). From each folder name, extract a leading 6-digit number matching `^(\d{6})\s*-` and ignore everything else — that regex naturally skips utility folders (`Employees`, `Client Documents`, `Sales & Marketing`, `Archive (Pre-Proest)`, the template folder itself) and bare year folders (`2021`...`2026`).

   Important: don't look *inside* the year folders (`2024`, `2025`, `2026`, etc.) for numbering — they're a stale/legacy structure and can contain duplicate or out-of-sequence numbers (e.g. `2026` contains a second, different `260010 -...` folder that has nothing to do with the live top-level `260010` job). The live, active sequence lives only in the top-level listing.

   Take the highest number found among the top-level matches, add 1, and zero-pad to 6 digits. If the user gives you a specific job number instead of wanting the next one auto-assigned, use theirs, but first confirm no top-level folder with that number already exists.

3. **Build the new folder name.**
   - With a tag: `{job number} - {name} [{tag}]`
   - Without a tag: `{job number} - {name}`

4. **Copy the template.** Call `mcp__Dropbox__copy` with:
   - `source_path`: `/BLDG/BLDG Estimating/Estimate Folder Template [COPY & PASTE ONLY]`
   - `destination_path`: `/BLDG/BLDG Estimating/{new folder name}`
   - `autorename: false` — if the copy fails because something already exists at that destination, stop and tell the user rather than letting Dropbox silently append " copy" or similar to the name.

5. **Confirm.** Tell the user the new folder's full name, e.g. "Created `260107 - 85 East Park Ave [Violante]` in BLDG Estimating."

## Why this matters

A wrong or duplicated job number causes real confusion later — it's the key that ties a folder to proposals, invoices, and whatever job list or accounting system references it. Don't guess at the number or the tag when the request is ambiguous; ask instead.
