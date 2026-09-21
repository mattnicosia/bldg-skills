---
name: proest-export-pdf-reports
description: Export ProEst PDF reports from a logged-in ProEst browser session. Use when asked to download, print, save, generate, or verify ProEst proposal PDFs, Schedule of Values PDFs, Estimate Cost Totals PDFs, or a small PDF report package for a named estimate/project/revision.
---

# ProEst PDF Reports Export

## Overview

Use a live Chrome/ProEst session plus Computer Use for ProEst UI interactions, macOS save dialogs, Finder, and Preview. This workflow is for printing ProEst reports to PDF and verifying the downloaded files. If ProEst is not logged in, pause and ask the user to log in; never request or store credentials.

Read `references/recording-evidence.md` if you need the original recorded report sequence or filename patterns.

## Inputs

Collect or infer:

- Target estimate/project name, estimate number, or revision.
- Report package to export. Default to:
  - `Proposals` -> `2. Proposal + Exclusions [Insert SOV]`.
  - `GC Schedule of Values` -> `Estimate Cost Totals`, grouped by `Subdivisions`.
- Output folder, defaulting to `Downloads`.
- Filename pattern, defaulting to `<Report_Name>_YYYY_MM_DD_<Estimate_or_Revision>.pdf`.

If multiple ProEst estimates match, ask the user to choose rather than guessing.

## Workflow

1. Open Chrome and navigate to `cloud.proest.com`.
2. Confirm ProEst is signed in. If the login page appears, ask the user to complete login.
3. Open the project/estimate list, such as Estimate Center or Active Estimates.
4. Search for the target estimate using the project name, estimate name, number, or revision.
5. Open the matching estimate and verify the Summary page heading/context matches the requested estimate.
6. Open Reports from the estimate navigation or navigate to `https://cloud.proest.com/company/reports`.
7. In Reports, ensure `Select Estimate` is set to the verified estimate if the field is blank or wrong.

## Export Proposal PDF

1. Expand `Proposals`.
2. Select `2. Proposal + Exclusions [Insert SOV]`, unless the user requested a different proposal report.
3. Click `Print`.
4. In the macOS save dialog, choose the output folder and save as `2._Proposal_+_Exclusions_[Insert_SOV]_YYYY_MM_DD_<Estimate_or_Revision>.pdf`.
5. Wait until Chrome shows the download/save has completed.

## Export Cost Totals PDF

1. Expand `GC Schedule of Values`.
2. Select `Estimate Cost Totals`, unless the user requested a different SOV report.
3. Open the grouping control if it shows `Divisions`; select `Subdivisions`.
4. Click `Print`.
5. In the macOS save dialog, choose the output folder and save as `Estimate_Cost_Totals_YYYY_MM_DD_<Estimate_or_Revision>.pdf`.
6. Wait until Chrome shows the download/save has completed.

## Verification

- Use Chrome's download control or Finder to show the saved PDFs in the output folder.
- Confirm both expected filenames are present.
- Open the proposal PDF in Preview when visual verification is useful. Verify page 1 indicates a proposal and Schedule of Values content for the target estimate.
- If inspecting the cost totals PDF, verify the visible title/content matches `Estimate Cost Totals`.
- Report saved file paths and any caveats, such as ambiguous estimate selection, missing report options, an unexpected grouping value, or failed downloads.

## Safety Notes

- Treat client names, estimate totals, proposal recipients, and account details as private. Use placeholders in reusable notes and summaries unless the user explicitly asks for exact filenames or paths.
- Prefer UI labels and page headings over coordinates.
- Do not overwrite an existing report unless the user confirms that replacing it is intended.
