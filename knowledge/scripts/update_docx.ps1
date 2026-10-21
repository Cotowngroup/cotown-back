# Opens every .docx in salida/ with Word, updates the table of contents and fields, and saves it.
# Usage (from knowledge/): pwsh scripts/update_docx.ps1 [-Pdf]   (-Pdf also exports a PDF next to each document)
param([switch]$Pdf)
$out = Join-Path (Split-Path $PSScriptRoot -Parent) 'salida'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  Get-ChildItem $out -Filter *.docx | Where-Object { $_.Name -notlike '~$*' } | ForEach-Object {
    $doc = $word.Documents.Open($_.FullName)
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) { $toc.UpdatePageNumbers() }
    $doc.Save()
    if ($Pdf) { $doc.ExportAsFixedFormat([System.IO.Path]::ChangeExtension($_.FullName, '.pdf'), 17) }
    "{0}: {1} páginas" -f $_.Name, $doc.ComputeStatistics(2)
    $doc.Close($false)
  }
} finally {
  $word.Quit()
}
