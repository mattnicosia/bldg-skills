# Workflow Playbook

A complete pass takes 5–15 minutes. Don't skip steps even when they feel obvious — the source materials often contradict themselves and asking is faster than fixing.

## Step 1: Read the source materials

The project folder is usually under:
```
C:\Users\Matt\Matt Nicosia Dropbox\BLDG\BLDG Estimating\<NNNNNN> - <Project Name> [<GC Name>]\Bid Documents\
```

Typical contents:
- An Outlook `.msg` file forwarded from the GC (containing the architect's original scope email at the bottom)
- One or more `.pdf` sketch plans or existing-conditions drawings
- Possibly a `.docx` brief or program

**Read the .msg via Outlook COM** (PowerShell):
```powershell
$outlook = New-Object -ComObject Outlook.Application
$mail = $outlook.Session.OpenSharedItem("path\to\file.msg")
Write-Output "FROM: $($mail.SenderName)"
Write-Output "SUBJECT: $($mail.Subject)"
Write-Output $mail.Body
```

**Read .pdfs via the Read tool** — for multi-page architectural drawings, just pass the path and the tool will render images you can interpret directly. If the PDF has a corrupt header (some emailed PDFs do), strip leading bytes:
```powershell
$bytes = [System.IO.File]::ReadAllBytes($src)
for($i=0; $i -lt 100; $i++){ if($bytes[$i] -eq 0x25 -and $bytes[$i+1] -eq 0x50 -and $bytes[$i+2] -eq 0x44 -and $bytes[$i+3] -eq 0x46){ $idx = $i; break } }
[System.IO.File]::WriteAllBytes($dst, $bytes[$idx..($bytes.Length-1)])
```

**Pull out**: project number, project address, architect firm + lead contact, GC contact, vague scope phrases ("the works," "redo bathrooms," "move the bar"), schedule hints ("reopen by end of 2026"), exclusions the architect mentioned ("storefront is on a different timeline").

## Step 2: Establish the project facts

Briefly summarize back to the user what you found, then ask for missing facts. The user knows the building; you do not. Confirm via `AskUserQuestion`:

**Round 1 — biggest cost-drivers first** (these swing the number by hundreds of thousands of dollars):

1. Finish tier — present as 4-option (casual / mid / high-end / range). Default to "range across two tiers" if "the works."
2. HVAC scope — full new / reuse + new distribution / allowance / show both as add-alt. Default: show both.
3. Bar scope — new custom in new location / relocate existing / refresh only / allowance. Default: new custom.
4. Kitchen scope — stays minimal / refresh finishes / reconfigure / equipment allowance. Default: stays minimal.

**Round 2 — boundaries and exclusions**:

5. Bathrooms — full ADA gut allowance / reconfigure / refresh / allowance only. Default: full gut allowance @ $85K/bath.
6. Scope in/out — confirm storefront/stair excluded, FF&E in/out, POS/AV/smallwares in/out.
7. MEP service — assume existing adequate / Con Ed upgrade allowance / sprinkler/FA scope.
8. Soft costs — confirm GC/GR/insurance/OH&P/contingency carried; permits + sales tax usually excluded.

**Round 3 — SF and schedule**:

9. SF — ask owner directly. Get FOH, kitchen, bath, circulation, cellar separately. Don't scale from drawings unless they confirm.
10. Schedule — months from NTP. 6 months for ~2,000 SF FOH gut, 9 months for ~5,000 SF.
11. Structural — usually NONE. Confirm explicitly.
12. Abatement — usually NONE. Confirm owner will provide ACM-clear letter.

Don't ask all twelve at once — batch 3–4 per `AskUserQuestion` call. If the user gives you an SF number in one answer, don't ask again. If they say "you decide," default to the recommended option.

## Step 3: Build the pricing model

Open `scripts/build_estimate.py` and edit the data section near the top:

- `OUT` — full output path to the .xlsx in `Bid Documents`
- `FOH_SF`, `GROSS_SF` — confirmed SF
- `PROJECT_NUMBER`, `PROJECT_NAME`, `PROJECT_ADDRESS`, `GC_NAME`, `ARCHITECT_NAME`, `OWNER_NAME`, `RECIPIENT_NAME`, `RECIPIENT_TITLE`
- `LINE_ITEMS` — list of (csi_code, description, tier_a, tier_b, is_header) tuples. Scale from the MacDougal baseline using SF ratio and adjust for scope differences.
- `HVAC_ALT` — list of (csi_code, description, tier_a, tier_b). Typically $185–210K for new RTUs/condensers + ~$70K for demo/rigging/electrical.
- `TAKEOFF` — list of (description, qty, unit, notes). Update SF-based quantities (demo, finishes, electrical branch wiring) to the new FOH SF.
- Markups stay at GC 7% / Fee 5% / Insurance 3% / Contingency 12% unless the user requests different.

See `pricing_logic.md` for how to derive line items from a benchmark.

## Step 4: Generate the workbook

Save the script to the project's Bid Documents folder, then run it via stdin pipe to bypass Windows sandbox file-execution restrictions:

```bash
cat build_estimate.py | py.exe - 2>&1 | tail -10
```

You should see a summary like:
```
Saved: C:\...\260079_MacDougal_Budgetary_Estimate_v1.xlsx
Tier A total: $1,916,430  ($896/SF FOH)
Tier B total: $2,485,390  ($1162/SF FOH)
Overall range: $1.92M (Tier A base) - $2.85M (Tier B + HVAC)
```

If you see `PermissionError: ... PIL\__init__.py`, Pillow is installed and broken — uninstall it: `py.exe -m pip uninstall -y Pillow`. Run this twice; once might not be enough if it's in both user and system site-packages.

## Step 5: Post-process and export PDF

Save `scripts/export_pdf.ps1` to the Bid Documents folder (or invoke directly from the skill assets path), edit the variables at top:

```powershell
$xlsx = "C:\path\to\<NNNNNN>_<ShortName>_Budgetary_Estimate_v<N>.xlsx"
$logo = "C:\path\to\OD_logo.png"
$pdfTmp = "C:\Users\<user>\estimate_v<N>.pdf"     # MUST be outside Dropbox
$projectTitle = "Estimate: <NNNNNN> <Project Name>"
$projectAddress = "<Address>, <City>, <State> <Zip>"
$footerText = "<GC Name> | <GC Address> | <GC Phone>"
$dateStr = "MM/dd/yyyy"
```

Run the script. It will:
- Open the workbook with Excel COM
- Recalculate all formulas
- For each sheet: set portrait orientation, Fit All Columns on One Page (FitToPagesWide=1, FitToPagesTall=False — these are the actual values that work, not 0), 0.7" L/R margins, 1.0" top, 0.75" bottom, header margin 0.3", footer margin 0.3", center horizontally
- Insert the logo image as the left print header (`LeftHeaderPicture.Filename = $logo`, `LeftHeader = "&G"`)
- Set right print header to project title + address (two lines, bold + italic)
- Set footer: left = date, center = GC contact line, right = "Page &P of &N"
- Save the workbook
- Export PDF to the temp path

After the PDF is created, move it into Bid Documents via Bash:
```bash
mv "/c/Users/<user>/estimate_v<N>.pdf" "<NNNNNN>_<ShortName>_Budgetary_Estimate_v<N>.pdf"
```

If Excel ever holds the file open from a previous run (PermissionError on save), kill it: `Get-Process -Name "EXCEL" | Stop-Process -Force`.

## Step 6: Draft the email reply

Use the template in `assets/email_template.txt` as a starting point and customize:
- To/Cc lines from the original .msg recipients
- Project name + address
- The four scenario totals (Tier A base, Tier A + HVAC, Tier B base, Tier B + HVAC)
- The overall budget range
- Scope highlights (full FOH gut + new bar + bath allowance + finishes/MEP)
- Standard schedule callout (months, design-development long-leads, expediter timing)
- Signature block (Ed Tassey / O+D Builders by default)

Save as `<NNNNNN>_<ShortName>_Email_Reply_Draft.txt` in Bid Documents.

## Step 7: Verify before reporting

Before telling the user the deliverable is ready, open the PDF (use the `Read` tool with the .pdf path) and confirm:
- Cover letter on page 1, scenario table visible, totals match the script output
- Logo on every page header
- No `####` or `#REF!` anywhere
- Footer "GC Builders | ..." reads cleanly (not "BLDG Estimating")
- Notes/exclusions page has the explicit "NO STRUCTURAL" and "NO ASBESTOS" assumptions
- Page count is 10–18 pages (more than that = something is wrapping wrong)

If anything is off, fix and bump version (v1 → v2 → v3). Don't deliver a broken PDF.

## Step 8: Summary to user

Report back with:
- Scenario table (4 rows: Tier A base / +HVAC / Tier B base / +HVAC)
- Overall range
- A brief sanity check vs. the Paolo benchmark
- 2–3 things to flag (assumptions worth confirming, items not carried)
- Names of the 3 output files

Then wait for corrections. Iterations are expected — the architect will push back on bath allowance, schedule, structural assumption, or finish tier. Apply changes, bump version, regenerate.
