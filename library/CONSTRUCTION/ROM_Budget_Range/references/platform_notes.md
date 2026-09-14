# Platform Notes

Bugs and quirks that will waste real time if you hit them blind.

**Two supported paths. Check which machine you are on before starting.**

| | macOS / Linux | Windows |
|---|---|---|
| Build workbook | `scripts/build_estimate.py` (openpyxl) | same |
| xlsx -> PDF | **`scripts/export_pdf.py`** (LibreOffice + PyMuPDF) | `scripts/export_pdf.ps1` (Excel COM) |
| Read `.msg` | `extract-msg` (pip) | Outlook COM |

---

# macOS / Linux path (default)

## Requirements

```bash
brew install --cask libreoffice      # provides `soffice`
python3 -m pip install PyMuPDF openpyxl
```

Pillow is fine here — install it if you want. The "uninstall Pillow" rule below is a
Windows-sandbox-only problem and does not apply on macOS.

## Generating the PDF

```bash
python3 scripts/export_pdf.py \
  --xlsx "<project>/Bid Documents/260105_620W52_Budgetary_Estimate_v1.xlsx" \
  --out  "<project>/Bid Documents/260105_620W52_Budgetary_Estimate_v1.pdf" \
  --logo assets/OD_logo.png \
  --title "Estimate: 260105 620 West 52nd Street" \
  --address "620-622 West 52nd Street, New York, NY 10019" \
  --date "07/30/2026"
```

Writing straight into a Dropbox path works fine — the Excel COM Dropbox bug is
Windows-only.

## How it replaces the Excel COM tricks

Excel's `LeftHeaderPicture` + `&G` placeholder made the logo repeat on every printed
page. **openpyxl cannot write header/footer images** — there is no equivalent. So:
LibreOffice paginates, then PyMuPDF stamps the logo, the title/address block, and the
footer onto every page. More predictable than Excel's header renderer, since positions
are exact points.

## Three real traps, all found by testing against the known-good Windows output

**1. Page setup must be normalized or money columns silently vanish.**
Excel writes `fitToWidth` as absent when set via COM, and often leaves a stale `scale`
alongside `fitToPage=True`. Excel ignores the stale scale; **LibreOffice honors it and
over-shrinks.** On 260093 v4 that produced 6 pages instead of 10 with **27 of 37 dollar
figures missing** — no error, no `###` markers, just absent numbers on a cost document.
`export_pdf.py` fixes this in `normalize_page_setup()` (explicit `fitToWidth=1`,
`fitToHeight=0`, `scale=None`) against a temp copy. Never disable that step.

**2. Hidden sheets are dropped from the PDF, by LibreOffice *and* by Excel.**
260093 v4 has its Takeoff tab hidden, so a re-export loses two whole pages of
quantities. `export_pdf.py` warns by name and offers `--include-hidden`. **Check that
warning every run** — a missing Takeoff section in a client deliverable is not
recoverable after it is sent.

**3. `insert_textbox` fails silently when text does not fit.**
PyMuPDF returns a negative number and renders *nothing* — no exception. A 51-character
title at 11pt needed ~311pt in a 256pt box, so the header vanished from every page and
the PDF still looked plausible. All stamping goes through `fit_text()`, which shrinks to
fit and prints a warning if it still cannot.

Also: pass the logo once and reuse its xref. Re-passing `filename=` per page re-embeds
the 81KB PNG on every page.

## Verification (do this whenever the pipeline changes)

Re-export the last known-good job and diff against its committed PDF:

```
260093 v4 target: 10 pages, 1 image xref, 73 numeric tokens
```

Compare page count, distinct image xrefs, and the set of numeric tokens. Extracting
money with a `\$[\d,]+` regex gives false alarms — LibreOffice renders accounting format
with the `$` as a separate text run, so `$90,000` extracts as `$` + `90,000`. Match on
digit groups, not on the dollar sign.

## Reading `.msg` on macOS

No Outlook COM. Use:

```bash
python3 -m pip install extract-msg
```

```python
import extract_msg
m = extract_msg.Message(path)
print(m.sender, m.to, m.subject, m.date)
print(m.body)
for a in m.attachments: print(a.longFilename)
```

If it is not installed and cannot be, ask the user to forward the email as `.eml` or
paste the text. Do not guess at the architect's scope.

---

# Windows path (legacy)

Everything below was encountered and solved during the MacDougal Street project. It
still applies when running on Windows with Excel installed.

## Python execution from Dropbox folders

**Problem:** Running `py.exe path/to/script.py` from within a Dropbox-synced folder often fails with `PermissionError: [Errno 13]` even when the file exists and your account owns it.

**Cause:** Some interaction between Dropbox's file lock and the sandbox's file-execution restriction.

**Fix:** Pipe the script content to Python via stdin, which bypasses the file-open step entirely:
```bash
cat scripts/build_estimate.py | py.exe - 2>&1 | tail -10
```

This works from any folder, including Dropbox.

## openpyxl crashes if Pillow is installed

**Problem:** `from openpyxl import Workbook` fails with `PermissionError: [Errno 13]: 'C:\\...\\PIL\\__init__.py'`.

**Cause:** openpyxl autoloads `openpyxl.drawing.image` which imports PIL. If Pillow is installed but its `__init__.py` is in a sandboxed-restricted path, the import fails. Without Pillow installed, openpyxl falls back to a no-image path that doesn't need PIL.

**Fix:** Uninstall Pillow before running the build:
```bash
py.exe -m pip uninstall -y Pillow
py.exe -m pip uninstall -y Pillow   # run twice if Pillow is in both user and system site-packages
```

**Do not install Pillow** as a "fix" — it makes things worse, not better. The build script never needs it (the logo is inserted via Excel COM print header, not as an embedded image).

## WebP to PNG conversion (when you need the logo from scratch)

**Problem:** The O+D logo at `Sales & Marketing\Client Logos\O+D+builders+logo.webp` is WebP format. openpyxl and System.Drawing don't read WebP. Pillow does but is broken (see above).

**Fix:** Use the Windows WinRT `BitmapDecoder` API via PowerShell, which has native WebP support on Win10+. See `scripts/extract_logo_from_webp.ps1`.

The bundled `assets/OD_logo.png` is pre-converted, so this script is only needed if the logo file changes.

## Excel COM PDF export silently fails into Dropbox

**Problem:** `$wb.ExportAsFixedFormat(0, $pdfPath, ...)` returns successfully but no file is created when `$pdfPath` is inside a Dropbox folder.

**Cause:** Unclear — likely a race between Excel COM and Dropbox's file lock, or a sandbox permission interaction. No error is thrown.

**Fix:** Export to a path outside Dropbox first (e.g., user home), then move with Bash:
```powershell
$pdfTmp = "C:\Users\Matt\estimate_temp.pdf"
$wb.ExportAsFixedFormat(0, $pdfTmp, 0, $true, $false)
```
```bash
mv "/c/Users/Matt/estimate_temp.pdf" "<project Bid Documents>/<filename>.pdf"
```

This works every time.

## Excel print setup property gotchas

When configuring `$ps = $worksheet.PageSetup` via COM in PowerShell:

```powershell
$ps.Orientation = 1     # xlPortrait
$ps.Orientation = 2     # xlLandscape

$ps.PaperSize = 1       # xlPaperLetter (8.5" x 11")

$ps.Zoom = $false       # MUST be set to false BEFORE FitToPages*
$ps.FitToPagesWide = 1  # Fit width to 1 page (the "Fit All Columns on One Page" preset)
$ps.FitToPagesTall = $false   # auto height — use $false, NOT 0 (0 throws "Unable to set...")
```

The order matters: set `Zoom = $false` first, then the `FitToPages*` properties. Otherwise Excel ignores them.

Other commonly-used:
```powershell
$ps.CenterHorizontally = $true
$ps.LeftMargin = $excel.InchesToPoints(0.7)
$ps.TopMargin = $excel.InchesToPoints(1.0)
$ps.HeaderMargin = $excel.InchesToPoints(0.3)
```

## Excel COM print header image

This is the magic that puts the O+D logo on every printed page automatically:

```powershell
$ps.LeftHeaderPicture.Filename = "C:\path\to\OD_logo.png"
$ps.LeftHeaderPicture.Height = 54       # points (~ 0.75")
$ps.LeftHeaderPicture.Width = 145       # points (~ 2")
$ps.LeftHeader = "&G"                    # the "&G" placeholder tells Excel to render the picture here
```

Without `$ps.LeftHeader = "&G"`, the picture is set but not displayed. With `&G`, it repeats on every printed page (this is built into Excel's page-header rendering).

For right-header text with formatting:
```powershell
$ps.RightHeader = "&""Arial,Bold""&10 Estimate: <project>`n&""Arial,Italic""&9 <address>"
```
- `&""Arial,Bold""` selects font + style
- `&10` sets size to 10pt
- `` `n `` (PowerShell backtick-n) is a literal newline within the header
- Don't escape these — PowerShell's double-quoted string handling does the right thing

## Killing zombie Excel processes

After a script crash or interruption, Excel sometimes leaves a hidden process holding the file:

```powershell
Get-Process -Name "EXCEL" -ErrorAction SilentlyContinue | Stop-Process -Force
```

Symptom: next run fails with `PermissionError` on the xlsx, or Excel COM hangs on `Workbooks.Open`. Killing the process clears it.

## PowerShell stop-parsing for cmdline args

If you ever need to pass args containing `-` or `@` to a native exe through PowerShell:
```powershell
git log --% --format=%H
```
The `--%` token tells PowerShell to stop parsing and pass everything after literally. Not usually needed for this skill but worth knowing.

## Reading Outlook .msg files

The `.msg` format is Microsoft-proprietary. The reliable parser is Outlook itself via COM:

```powershell
$outlook = New-Object -ComObject Outlook.Application
$mail = $outlook.Session.OpenSharedItem($msgPath)
Write-Output "FROM: $($mail.SenderName) <$($mail.SenderEmailAddress)>"
Write-Output "TO: $($mail.To)"
Write-Output "SUBJECT: $($mail.Subject)"
Write-Output "SENT: $($mail.SentOn)"
Write-Output $mail.Body                  # plain text
# Write-Output $mail.HTMLBody            # HTML version if needed
foreach($a in $mail.Attachments){ Write-Output $a.FileName }
```

This works on any Windows machine with Outlook installed. The shell CWD resets after this call (Outlook COM does some chdir-like behavior), so don't rely on `pwd` after.

## PDF Read fallback

The `Read` tool can read PDFs natively but on this machine it sometimes errors with `pdftoppm failed`. When that happens, just call `Read` without the `pages` parameter — it falls back to the embedded text extraction, which is fine for everything except heavily image-based PDFs.

For image-based PDFs (architectural drawings, scans), the embedded reader returns garbled extraction. In that case there's no good fallback in the current sandbox — note it to the user and proceed with whatever you can gather from the email/scope description.
