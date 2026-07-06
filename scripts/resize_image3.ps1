Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile("C:\Users\Administrator\.openclaw\media\inbound\9797fb19-7c88-4aa3-b91d-6803cdc04e01.jpg")
$width = [int]($img.Width * 0.3)
$height = [int]($img.Height * 0.3)
$thumb = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($thumb)
$graphics.DrawImage($img, 0, 0, $width, $height)
$thumb.Save("C:\Users\Administrator\.openclaw\media\inbound\9797fb19-thumb.jpg", [System.Drawing.Imaging.ImageFormat]::Jpeg)
$graphics.Dispose()
$thumb.Dispose()
$img.Dispose()
Write-Host "Done: $width x $height"
