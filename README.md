# Discord TypeScript Bot Template

This is a simple bot built to be developed further for personal needs. Or, if you wish, a standalone bot for server tasks.

## Running

To run this bot, you will need the following:
- [Bun](https://bun.com/docs/installation)
- Git
- NodeJS

Clone the repository:

```bash
git clone https://github.com/LittleT6109/discord-ts-bot
cd discord-ts-bot
```

Create `.env.local` using `.env.local.example` as a template, then add your [bot credentials](https://github.com/LittleT6109/discord-ts-bot#getting-bot-credentials).

Edit `src/config.ts` to match your needs.

Install bot dependencies:
```bash
bun i
```

Compile the files into JavaScript:
```bash
bun run build
```

Sync the bot commands:
```bash
bun run sync
```

Start the bot:
```bash
bun run start
```

## Getting Bot Credentials

1. Go to https://discord.com/developers/applications
2. Create a new application
3. Copy the Application ID into .env.local
4. Open the Bot tab and reset/copy the token
5. Add the token to .env.local
