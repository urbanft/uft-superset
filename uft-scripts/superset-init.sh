#!/bin/sh

set -eu

echo "============================================================"
echo "Superset initialization"
echo "============================================================"

echo ""
echo "Running Superset DB upgrade..."

superset db upgrade

echo ""
echo "Creating admin user..."

superset fab create-admin \
  --username "${SUPERSET_ADMIN_USERNAME:-admin}" \
  --firstname "${SUPERSET_ADMIN_FIRSTNAME:-Ravi}" \
  --lastname "${SUPERSET_ADMIN_LASTNAME:-Pratap}" \
  --email "${SUPERSET_ADMIN_EMAIL:-rpratap@uft-int.com}" \
  --password "${SUPERSET_ADMIN_PASSWORD:-Test@123}"

echo ""
echo "Initializing Superset..."

superset init

echo ""
echo "============================================================"
echo "Superset initialization completed successfully."
echo "============================================================"
