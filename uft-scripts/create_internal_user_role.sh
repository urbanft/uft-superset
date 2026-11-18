#!/bin/bash

set -e

echo "Running InternalUser role configuration..."

superset shell <<'PYTHON'
exec(open("/app/create_internal_user_role.py").read())
PYTHON

echo "InternalUser role configuration completed."
