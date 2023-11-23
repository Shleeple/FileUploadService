param(
    #[Parameter(Mandatory=$true)]
    [string]$m
)

# Activate the virtual environment
& .venv\Scripts\Activate.ps1
# Freeze pip packages to requirements.txt
pip freeze > .\UploadFiles\requirements.txt

# Write progress to the console
Write-Host "Created requirements file"

# Create an array of files to add to Git repository
$files = @(
    ".\UploadFiles",
    "Push-GitChanges.ps1"
)
# Add specified files to Git repository
foreach ($file in $files) {
    git add $file
}

# Write progress to the console
Write-Host "Added needed files to staging area"

# set commit message
$currentDate = get-date -format "yyyy-MM-dd HH:mm:ss"
if ($m) {
    $commitMessage = "$m - $currentDate"
} else {
    $commitMessage = "Pushed changes from local repo to Git repository - $currentDate"
}
# commit changes
git commit -m $commitMessage
# push changes to remote repository
git push origin main

# Write progress to the console
Write-Host "Pushed changes from local repo to Git repository"