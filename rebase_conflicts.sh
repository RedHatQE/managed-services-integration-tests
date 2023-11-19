#!/bin/bash

# Function to check if there are any conflicts
function check_conflicts() {
  if git diff --quiet --cached; then
    return 1 # No conflicts
  else
    return 0 # Conflicts exist
  fi
}

# Function to perform an "accept-theirs" resolve for each conflicting file
function resolve_conflicts() {
  git diff --name-only --cached | while read -r file; do
    git checkout --theirs -- "$file"
    git add "$file"
  done
}

# Main rebase function
function rebase_main_to_branch() {
  git checkout main
  git pull origin main
  git checkout acm-observability
  git pull origin acm-observability
  git rebase main

  while check_conflicts; do
    echo "Conflicts found. Resolving conflicts with 'accept-theirs' strategy."
    resolve_conflicts
    git rebase --continue
  done

  echo "Rebase completed successfully."
}

# Run the rebase
rebase_main_to_branch
