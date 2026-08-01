FROM oven/bun:1 AS builder

WORKDIR /app

# Install dependencies
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile

# Copy source and build
COPY . .
RUN bun run build



FROM oven/bun:1-slim

WORKDIR /app

# Needed so `bun run start` works
COPY --from=builder /app/package.json ./

# Copy only the built output
COPY --from=builder /app/dist ./dist

CMD ["bun", "run", "start"]