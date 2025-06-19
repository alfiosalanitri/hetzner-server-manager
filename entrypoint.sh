#!/bin/sh

# This script is executed every time the container starts.

# Exit immediately if a command exits with a non-zero status.
set -e

# Apply database migrations
echo "Applying database migrations..."
flask db upgrade

exec "$@"