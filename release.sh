#!/bin/bash

set -e

if [[ -z "$1" ]]; then
  echo "Usage: ./release.sh vX.Y.Z"
  exit 1
fi

VERSION="$1"

if ! [[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Version must follow semantic versioning format, e.g., v1.0.0"
  exit 1
fi

if ! git diff-index --quiet HEAD --; then
  echo "Uncommitted changes detected. Staging and committing..."
  git add .
  git commit -m "Release $VERSION"
fi

git tag "$VERSION"
git push origin "$VERSION"

echo ""
echo "✅ Tag $VERSION pushed!"
echo "The Docker image will be available at:"
echo "  ghcr.io/alfiosalanitri/hetzner-server-manager:$VERSION"
echo "  ghcr.io/alfiosalanitri/hetzner-server-manager:latest"