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

# Copy only the built output
COPY --from=builder /app/dist ./

RUN chmod -R 777 /app

CMD ["bun", "bot.js"]
