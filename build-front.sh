#!/usr/bin/env bash -ex

BASEDIR=$(dirname "$0")
VERSION=$(awk '{ sub(/.*\//, ""); print }' <<< $(git rev-parse --abbrev-ref HEAD))
cd front
npm install --legacy-peer-deps
sed -i '' -e s/\"version\":\ \"0.0.0-dev\"/\"version\":\ \"$VERSION\"/g package.json

# When running on macOS Big Sur
# export NODE_OPTIONS=--openssl-legacy-provider
npm run build --production

