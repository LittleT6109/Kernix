#!/usr/bin/env bash
set -e

# Run Bun's build command
bun build src/index.ts \
  --outfile dist/bot.js \
  --target bun \
  --minify

# Bundle the default config alongside the built output so runtime can create data/config.toml
mkdir -p dist/defaults
cp src/config.toml dist/defaults/config.toml

# Copy the license
cp LICENSE dist
