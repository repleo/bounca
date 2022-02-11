#!/usr/bin/env bash -ex

BASEDIR=$(dirname "$0")
VERSION=$(awk '{ sub(/.*\//, ""); print }' <<< "$CI_COMMIT_REF_NAME")

if [[ $VERSION =~ ^([0-9]\.?)+$ ]]; then
    echo ""
else
    VERSION="0.0.0-$VERSION"
fi

echo $VERSION

cd front

sed -ri "s|\"version\":\ \"0.0.0-dev\"|\"version\":\ \"$VERSION\"|g" package.json

# npm modules are already fetched
# npm install --legacy-peer-deps
# When facing error:0308010C:digital envelope routines::unsupported add this export
export NODE_OPTIONS=--openssl-legacy-provider
npm run build --production

