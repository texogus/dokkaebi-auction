#!/usr/bin/env bash
set -euo pipefail

npm_config_cache=/private/tmp/npm-cache npm install
npm run build:mac
/usr/bin/ditto -c -k --sequesterRsrc --keepParent \
  "dist-electron/DokkaebiAuction-darwin-x64/DokkaebiAuction.app" \
  "dist-electron/DokkaebiAuction-mac-test.zip"
