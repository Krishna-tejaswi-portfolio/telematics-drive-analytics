#!/usr/bin/env bash
set -e
superset fab create-admin \
  --username admin --firstname a --lastname b --email admin@example.com --password admin
superset db upgrade
superset init
