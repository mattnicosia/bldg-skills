# Convert a WebP image to PNG using Windows WinRT BitmapDecoder.
#
# Use this only when you need to regenerate the bundled OD_logo.png — e.g.,
# the source logo at "Sales & Marketing\Client Logos\O+D+builders+logo.webp"
# changes, or you need a logo for a different GC client.
#
# Why not Pillow? Installing Pillow on this Windows + sandbox setup breaks
# openpyxl (it tries to import PIL but the path is restricted). The WinRT
# approach uses Windows' built-in WebP codec, no Python dependency.
#
# Why not System.Drawing? GDI+ doesn't support WebP natively.
#
# Usage: edit the $src and $dst paths and run. Save the output to a non-Dropbox
# path first; Dropbox sometimes 0-bytes the file during writes.

$src = "C:\Users\Matt\Matt Nicosia Dropbox\BLDG\BLDG Estimating\Sales & Marketing\Client Logos\O+D+builders+logo.webp"
$dst = "C:\Users\Matt\OD_logo.png"   # temp path, move to skill assets after

if(Test-Path $dst){ Remove-Item $dst -Force }

# Load WinRT types
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
Add-Type -AssemblyName System.Runtime.WindowsRuntime
Add-Type -AssemblyName System.Drawing

# Helper to await WinRT IAsyncOperation<T> from PowerShell
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]

function Await($WinRtTask, $ResultType){
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

# Decode WebP
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($src)) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync('Read')) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$w = $decoder.PixelWidth
$h = $decoder.PixelHeight
Write-Output "Decoded: ${w}x${h} format: $($decoder.BitmapPixelFormat)"

$pixelData = Await ($decoder.GetPixelDataAsync()) ([Windows.Graphics.Imaging.PixelDataProvider])
$bytes = $pixelData.DetachPixelData()

# WinRT returns RGBA byte order; System.Drawing's Format32bppArgb expects BGRA.
# Swap R and B for each pixel.
for($i = 0; $i -lt $bytes.Length; $i += 4){
    $r = $bytes[$i]
    $bytes[$i] = $bytes[$i + 2]
    $bytes[$i + 2] = $r
}

# Build System.Drawing.Bitmap and save as PNG
$bmp = New-Object System.Drawing.Bitmap($w, $h, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$rect = New-Object System.Drawing.Rectangle(0, 0, $w, $h)
$bmpData = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::WriteOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
[System.Runtime.InteropServices.Marshal]::Copy($bytes, 0, $bmpData.Scan0, $bytes.Length)
$bmp.UnlockBits($bmpData)
$bmp.Save($dst, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

Start-Sleep -Milliseconds 500
if(Test-Path $dst){
    Write-Output "Saved: $dst ($((Get-Item $dst).Length) bytes)"
    Write-Output ""
    Write-Output "Next step: move to skill assets (via Bash):"
    Write-Output "  mv `"/c/Users/Matt/OD_logo.png`" `"/c/Users/Matt/.claude/skills/od-budgetary-estimate/assets/OD_logo.png`""
} else {
    Write-Output "ERROR: Output file not created."
}
