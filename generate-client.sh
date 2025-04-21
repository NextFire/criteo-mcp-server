#!/bin/sh -xe
SERVICE=${1:-retailmedia}
VERSION=${2:-preview}
rm -rf criteo-api/
uvx openapi-generator-cli[jdk4py] generate \
    -g python \
    -i https://api.criteo.com/$VERSION/$SERVICE/open-api-specifications.json \
    -o criteo-api \
    --remove-operation-id-prefix \
    -p projectName=criteo-api,packageName=criteo_api,library=asyncio
