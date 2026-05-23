#!/usr/bin/env bash
set -euo pipefail

npm_config_cache=/private/tmp/npm-cache npm install
npm run build:mac
/usr/bin/ditto -c -k --sequesterRsrc --keepParent \
  "dist-electron/도깨비경매-darwin-x64/도깨비경매.app" \
  "dist-electron/도깨비경매-electron-mac-test.zip"
