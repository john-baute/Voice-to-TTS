# Script to download and install the small Vosk model
Write-Host "Starting Vosk model download and installation..."

$modelUrl = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
$zipFile = "vosk-model-small-en-us.zip"
$modelDir = "vosk-model-small-en-us"

# Download the model
Write-Host "Downloading Vosk model from $modelUrl..."
try {
    Invoke-WebRequest -Uri $modelUrl -OutFile $zipFile
    Write-Host "Download completed successfully."
} catch {
    Write-Error "Failed to download the model: $_"
    exit 1
}

# Extract the model
Write-Host "Extracting model files..."
try {
    Expand-Archive -Path $zipFile -DestinationPath $modelDir -Force
    Write-Host "Extraction completed successfully."
} catch {
    Write-Error "Failed to extract the model: $_"
    exit 1
}

# Clean up the zip file
Write-Host "Cleaning up..."
try {
    Remove-Item $zipFile
    Write-Host "Zip file removed successfully."
} catch {
    Write-Host "Warning: Could not remove zip file: $_"
}

Write-Host "Installation completed successfully!"
Write-Host "The Vosk model is installed in: $modelDir"