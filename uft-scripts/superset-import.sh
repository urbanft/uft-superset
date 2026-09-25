#!/bin/sh

set -eu

# ------------------------------------------------------------
# Validate required environment variables
# ------------------------------------------------------------

: "${SUPERSET_ADMIN_USERNAME:?SUPERSET_ADMIN_USERNAME is required}"

: "${CLICKHOUSE_HOST:?CLICKHOUSE_HOST is required}"
: "${CLICKHOUSE_PORT:?CLICKHOUSE_PORT is required}"
: "${CLICKHOUSE_DATABASE:?CLICKHOUSE_DATABASE is required}"
: "${CLICKHOUSE_USERNAME:?CLICKHOUSE_USERNAME is required}"
: "${CLICKHOUSE_PASSWORD:?CLICKHOUSE_PASSWORD is required}"

echo "============================================================"
echo "Superset asset import"
echo "============================================================"

# ------------------------------------------------------------
# Superset data sources
#
# This is application configuration maintained with the code.
# Override through the environment only when required.
# ------------------------------------------------------------

if [ -z "${SUPERSET_DATA_SOURCES:-}" ]; then
    SUPERSET_DATA_SOURCES='{
      "name": "analyticsdb",
      "datasets": [
        "access_logs"
      ]
    }'
fi

export SUPERSET_DATA_SOURCES

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

ASSETS_DIR="${SUPERSET_ASSETS_DIR:-/app/assets/dashboards}"
REPLACE_SCRIPT="${SUPERSET_REPLACE_SCRIPT:-/app/replace_superset_assets.py}"

SUPERSET_URL="${SUPERSET_URL:-http://localhost:8088}"
SUPERSET_ADMIN_USERNAME="${SUPERSET_ADMIN_USERNAME:-admin}"

echo ""
echo "Configuration:"
echo "  Assets directory : ${ASSETS_DIR}"
echo "  Replace script   : ${REPLACE_SCRIPT}"
echo "  Superset URL     : ${SUPERSET_URL}"
echo "  Import user      : ${SUPERSET_ADMIN_USERNAME}"

# ------------------------------------------------------------
# Validate required commands/files
# ------------------------------------------------------------

echo ""
echo "Checking required commands..."

command -v curl >/dev/null 2>&1 || {
    echo "ERROR: curl is not installed."
    exit 1
}

command -v unzip >/dev/null 2>&1 || {
    echo "ERROR: unzip is not installed."
    exit 1
}

command -v zip >/dev/null 2>&1 || {
    echo "ERROR: zip is not installed."
    exit 1
}

command -v python >/dev/null 2>&1 || {
    echo "ERROR: python is not installed."
    exit 1
}

command -v superset >/dev/null 2>&1 || {
    echo "ERROR: superset command is not available."
    exit 1
}

if [ ! -f "$REPLACE_SCRIPT" ]; then
    echo "ERROR: Replace script not found:"
    echo "  $REPLACE_SCRIPT"
    exit 1
fi

if [ ! -d "$ASSETS_DIR" ]; then
    echo "ERROR: Dashboard assets directory not found:"
    echo "  $ASSETS_DIR"
    exit 1
fi

# ------------------------------------------------------------
# Wait for Superset
# ------------------------------------------------------------

echo ""
echo "Waiting for Superset..."

until curl -sf "${SUPERSET_URL}/health" >/dev/null 2>&1; do
    echo "Superset is not ready yet..."
    sleep 3
done

echo "Superset is ready."

# ------------------------------------------------------------
# Find dashboard bundle
# ------------------------------------------------------------

echo ""
echo "Searching for dashboard export..."

BUNDLE="$(
    find "$ASSETS_DIR" \
        -maxdepth 1 \
        -type f \
        -name '*.zip' \
        -print \
        | sort \
        | head -n 1
)"

if [ -z "$BUNDLE" ]; then
    echo "ERROR: No dashboard ZIP found in:"
    echo "  $ASSETS_DIR"
    exit 1
fi

echo "Source bundle:"
echo "  $BUNDLE"

# ------------------------------------------------------------
# Create temporary working directory
# ------------------------------------------------------------

WORK_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "$WORK_DIR"
}

trap cleanup EXIT INT TERM

echo ""
echo "Working directory:"
echo "  $WORK_DIR"

# ------------------------------------------------------------
# Extract bundle
# ------------------------------------------------------------

echo ""
echo "Extracting dashboard bundle..."

unzip -q "$BUNDLE" -d "$WORK_DIR"

echo "Bundle extracted."

# ------------------------------------------------------------
# Modify database/dataset configuration
# ------------------------------------------------------------

echo ""
echo "Updating database and dataset configuration..."

python "$REPLACE_SCRIPT" "$WORK_DIR"

echo ""
echo "Superset bundle configuration updated."

# ------------------------------------------------------------
# Locate actual Superset bundle root
#
# Do NOT assume the ZIP contains a particular top-level
# directory name.
# ------------------------------------------------------------

echo ""
echo "Locating Superset bundle root..."

BUNDLE_ROOT="$(
    find "$WORK_DIR" \
        -type f \
        -name 'metadata.yaml' \
        -print \
        | head -n 1 \
        | xargs -r dirname
)"

if [ -z "$BUNDLE_ROOT" ]; then
    echo "ERROR: Could not find metadata.yaml in extracted bundle."
    exit 1
fi

echo "Superset bundle root:"
echo "  $BUNDLE_ROOT"

# ------------------------------------------------------------
# Validate bundle structure
# ------------------------------------------------------------

echo ""
echo "Validating Superset bundle structure..."

if [ ! -f "$BUNDLE_ROOT/metadata.yaml" ]; then
    echo "ERROR: metadata.yaml not found."
    exit 1
fi

if [ ! -d "$BUNDLE_ROOT/databases" ]; then
    echo "ERROR: databases directory not found."
    exit 1
fi

if [ ! -d "$BUNDLE_ROOT/datasets" ]; then
    echo "ERROR: datasets directory not found."
    exit 1
fi

if [ ! -d "$BUNDLE_ROOT/charts" ]; then
    echo "ERROR: charts directory not found."
    exit 1
fi

if [ ! -d "$BUNDLE_ROOT/dashboards" ]; then
    echo "ERROR: dashboards directory not found."
    exit 1
fi

echo "Bundle structure:"
echo "  ✓ metadata.yaml"
echo "  ✓ databases/"
echo "  ✓ datasets/"
echo "  ✓ charts/"
echo "  ✓ dashboards/"

# ------------------------------------------------------------
# Import bundle
# ------------------------------------------------------------

echo ""
echo "Importing complete Superset bundle..."

superset import_directory \
    "$BUNDLE_ROOT" \
    --username "$SUPERSET_ADMIN_USERNAME" \
    --overwrite

echo ""
echo "============================================================"
echo "Superset asset import completed successfully."
echo "============================================================"
