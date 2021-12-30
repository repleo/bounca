#!/usr/bin/env bash -ex

BASEDIR=$(dirname "$0")
VERSION=$(awk '{ sub(/.*\//, ""); print }' <<< "$CI_COMMIT_REF_NAME")

echo "$VERSION"

if [ "$VERSION" == "master" ]; then
    VERSION="0.0.0-$VERSION"
fi


cd front
# npm install --legacy-peer-deps
ls

cat package.json

sed -ri '' -e "s|\"version\":\ \"0.0.0-dev\"|\"version\":\ \"$VERSION\"|g" package.json

cat package.json
npm install --legacy-peer-deps
# When running on macOS Big Sur
# export NODE_OPTIONS=--openssl-legacy-provider
npm run build --production

