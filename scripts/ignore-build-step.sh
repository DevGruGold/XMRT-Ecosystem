#!/bin/bash

# Vercel Ignored Build Step Script
# accurate determination of whether a build is necessary based on changed files

echo "VERCEL_GIT_COMMIT_REF: $VERCEL_GIT_COMMIT_REF"
echo "VERCEL_GIT_PREVIOUS_SHA: $VERCEL_GIT_PREVIOUS_SHA"
echo "VERCEL_GIT_COMMIT_SHA: $VERCEL_GIT_COMMIT_SHA"

if [ "$VERCEL_GIT_COMMIT_REF" == "main" ]; then
  # Build main branch if there are changes in app/, api/, or vercel.json
  # git diff --quiet returns 1 if there are changes, 0 if no changes
  # We want to return 1 (proceed with build) if there ARE changes
  # We want to return 0 (ignore build) if there are NO changes
  
  if git diff --quiet HEAD^ HEAD ./app/ ./api/ ./vercel.json; then
    echo "No changes in app/, api/, or vercel.json. Skipping build."
    exit 0
  else
    echo "Changes detected. Proceeding with build."
    exit 1
  fi
else
  # Always build for non-main branches (PRs, feature branches)
  echo "Non-main branch. Proceeding with build."
  exit 1
fi
