<div align="left">
  <table>
    <tr>
      <td>
        <img src="https://avatars.githubusercontent.com/u/309730965?s=200&v=4" alt="Kernix Logo" width="150">
      </td>
      <td>
        <h1 style="color: #3fff2e; margin: 0; font-size: 32px;">Kernix</h1>
        <p style="color: oklch(90% 0 0); font-size: 14px; margin: 5px 0;">Discord Bot for Nerds.<br>
        Tech news, fun commands, much more!</p>
      </td>
    </tr>
  </table>
</div>

## The purpose of this bot

I created this bot for tech-focused Discord servers. It includes the standard moderation commands you'd expect, along with fun and useful utilities aimed at developers and enthusiasts.

## Roadmap

- [ ] Add RSS feed tracking
- [ ] Add optional AI command
- [ ] Improve moderation system
  - [ ] Add warn system
  - [ ] Add action logging to user-configured channel
  - [ ] Add message delete/edit logging
- [ ] Add customizable welcome messages
- [ ] Add webpage with OAuth for users to change configuration, and other features

## Running

To run this bot, you will need the following:

- [Bun](https://bun.com/docs/installation)
- Git
- NodeJS

Clone the repository:

```bash
git clone https://github.com/LittleT6109/Kernix
cd Kernix
```

Create `.env.local` using `.env.local.example` as a template, then add your [bot credentials](https://github.com/LittleT6109/Kernix#getting-bot-credentials).

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
3. Copy the Application ID into `.env.local`
4. Open the Bot tab and reset the token, copy it
5. Add the token to `.env.local`
