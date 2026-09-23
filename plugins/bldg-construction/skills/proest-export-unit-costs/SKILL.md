---
name: proest-export-unit-costs
description: Export ProEst estimate unit-cost reports from a logged-in ProEst browser session. Use when asked to download, save, generate, or export an Estimate Unit Costs Excel report, unit-cost report, or similar ProEst report for a named estimate/project/revision.
---

# ProEst Unit Costs Export

## Overview

Use a live browser session to export a ProEst Excel report for a target estimate. Prefer an existing logged-in Chrome session because ProEst authentication and the macOS save dialog are part of the workflow. If ProEst is not logged in, ask the user to complete login; do not request or store credentials.

Read `references/recording-evidence.md` if you need the original captured example or filename pattern.

## Inputs

Collect or infer:

- Target estimate/project name, number, or revision.
- Report item, defaulting to `Estimate Unit Costs`.
- Report group, defaulting to `Internal Report for GC/Sub`.
- Group-by option, defaulting to the current ProEst default unless the user specifies one.
- Output folder, defaulting to `Downloads`.
- Filename, defaulting to `Estimate_Unit_Costs_YYYY_MM_DD_<estimate-name-or-revision>`.

## Workflow

1. Open ProEst in Chrome. Use the current tab if it is already on `cloud.proest.com`; otherwise navigate to ProEst and wait for the app to load.
2. Confirm the user is signed in. If a login page appears, pause and ask the user to log in.
3. Open the estimate search/list, such as Active Estimates or Estimate Center. Search using the supplied project name, estimate name, number, or revision.
4. Open the matching estimate and verify the Summary page heading contains the intended estimate. Check visible context such as estimate number, revision/name, status, and type before exporting.
5. Open Reports from the estimate navigation or go directly to `https://cloud.proest.com/company/reports`.
6. In Reports, set the `Select Estimate` field to the verified estimate if it is blank or set to another estimate.
7. Locate and expand the report group. For the recorded workflow this was `Internal Report for GC/Sub`.
8. Select the report item. For the recorded workflow this was `Estimate Unit Costs`.
9. Click the `Excel` export action in the Reports toolbar.
10. In the macOS save dialog, choose the output folder, set the filename, and confirm Save. Preserve any extension Chrome or ProEst adds automatically.
11. Wait for the browser download indicator to finish. If a second save prompt appears, verify it is for the same intended export before confirming; avoid creating accidental duplicates.

## Verification

- Confirm the file exists in the chosen folder with the intended name or the browser-appended Excel extension.
- If possible, open or inspect the downloaded workbook enough to verify it is the requested ProEst report and estimate.
- Report the saved path and any caveats, such as login required, ambiguous search results, duplicate prompts, or download failure.

## Safety Notes

- Treat ProEst credentials, personal email addresses, client data, and estimate financial details as sensitive. Do not include them in reusable instructions or summaries.
- Use stable UI labels, page headings, fields, and report names before resorting to coordinates.
- If multiple estimates match, ask the user to choose rather than guessing from similar names.
