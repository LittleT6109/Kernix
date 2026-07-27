#!/usr/bin/env bash
set -e

# Grab environment variables
source .env.local

# Run Bun's build command, injecting the environment variables we grabbed
bun build src/index.ts \
  --outfile dist/bot.js \
  --target node \
  --minify \
  --define "process.env.DISCORD_TOKEN='\"$DISCORD_TOKEN\"'" \
  --define "process.env.DISCORD_CLIENT_ID='\"$DISCORD_CLIENT_ID\"'"
