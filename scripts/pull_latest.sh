#!/bin/bash

# Check for Github Token environment variable
if [ -z "$GITHUB_TOKEN" ]; then
   echo "Error: GITHUB_TOKEN not set"
   exit 1
fi

# Authenticate with Github using Github Token environment variable
if ! gh auth status &>/dev/null; then
  gh auth login --with-token < $GITHUB_TOKEN
fi

# Get latest version numbers
FE_ARTIFACT=$(gh api repos/YOUR_USER/YOUR_REPO/actions/artifacts \
  | jq '.artifacts[] | select(.name | startswith("frontend-image-")) | {name: .name, id: .id}' | head -n2)
BE_ARTIFACT=$(gh api repos/YOUR_USER/YOUR_REPO/actions/artifacts \
  | jq '.artifacts[] | select(.name | startswith("backend-image-")) | {name: .name, id: .id}' | head -n2)

FE_ID=$(echo $FE_ARTIFACT | jq '.id')
BE_ID=$(echo $BE_ARTIFACT | jq '.id')

# Download and load
gh api repos/YOUR_USER/YOUR_REPO/actions/artifacts/$FE_ID/zip --output frontend.zip
gh api repos/YOUR_USER/YOUR_REPO/actions/artifacts/$BE_ID/zip --output backend.zip

unzip frontend.zip
unzip backend.zip

FE_VERSION=$(cat version.txt)
BE_VERSION=$(cat version.txt)

docker load < frontend.tar.gz
docker load < backend.tar.gz

echo "Frontend version: $FE_VERSION"
echo "Backend version: $BE_VERSION"