<#
The purpose of this script is to pull changes from 
the remote repository to the local repository.
#>

# Write progress to the console
Write-Host "Pulling changes from remote repo to local repo"

# Pull changes from remote repository
try {
    git pull origin main
    Write-Host "Successfully pulled changes from remote repo to local repo"
} 
catch {
    Write-Host "Error occurred while pulling changes from remote repo to local repo: $_"
}