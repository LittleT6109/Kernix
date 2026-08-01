#!/usr/bin/env bash
set -e

# Run Bun's build command
bun build src/index.ts \
  --outfile dist/bot.js \
  --target bun \
  --minify

# Copy the config into dist
cp src/config.toml dist/