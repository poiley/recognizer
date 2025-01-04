#!/bin/bash

# Export versions for docker-compose
export FE_VERSION=$(node -p "require('./frontend/package.json').version")
export BE_VERSION=$(cat backend/version)

./scripts/clean_local.sh
./scripts/build_local.sh
exit 0