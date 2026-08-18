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

## Features

- Commands:
  | Command                                    | Description                                    |
  | ------------------------------------------ | ---------------------------------------------- |
  | Message                                    | Send a message as the bot (Trusted users only) |
  | Slow                                       | Set the channel slowmode                       |

  Along with the standard moderation toolset

## Running

## Linux

### Docker

You will need the following:

- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/#plugin-linux-only)

Download the Docker Compose file:

```bash
curl -L -O https://github.com/LittleT6109/Kernix/releases/latest/download/docker-compose.yml
```

or

```bash
wget https://github.com/LittleT6109/Kernix/releases/latest/download/docker-compose.yml
```

Create `.env` using `.env.example` as a template, then set your [bot credentials](https://github.com/LittleT6109/Kernix#getting-bot-credentials), and NTFY credentials if using.

Start the Docker container:

```bash
docker compose up -d
```

Edit `kernix/config.toml` to match your needs, then restart the bot.

```bash
docker compose down
docker compose up -d
```

### Bun

You will need the following:

- [Bun](https://bun.com/docs/installation)
- Git
- NodeJS

Clone the repository:

```bash
git clone https://github.com/LittleT6109/Kernix
cd Kernix
```

Install dependencies:

```bash
bun i
```

Build the bot:

```bash
bun run build
```

Create `.env` using `.env.example` as a template, then set your [bot credentials](https://github.com/LittleT6109/Kernix#getting-bot-credentials), and NTFY credentials if using.

Run the bot:

```bash
bun run start
```

Edit `dist/data/config.toml` to match your needs, then restart the bot.

## Windows

Docker Compose CLI is only available on Linux, so you must use the Bun method here.

You will need the following:

- [Bun](https://bun.com/docs/installation)
- Git
- NodeJS

Clone the repository:

```bash
git clone https://github.com/LittleT6109/Kernix
cd Kernix
```

Install dependencies:

```bash
bun i
```

Build the bot:

```bash
bun run build
```

Create `.env` using `.env.example` as a template, then set your [bot credentials](https://github.com/LittleT6109/Kernix#getting-bot-credentials), and NTFY credentials if using.

Run the bot:

```bash
bun run start
```

Edit `dist/data/config.toml` to match your needs, then restart the bot.

## Getting Bot Credentials

1. Go to https://discord.com/developers/applications
2. Create a new application
3. Copy the Application ID into `.env`
4. Open the Bot tab and reset the token, copy it
5. Add the token to `.env`

<!-- TODO: Add instructions to get NTFY credentials, along with how to set up self-hosted NTFY -->

## Roadmap

- [ ] Add RSS feed tracking
- [ ] Add optional AI command
- [ ] Improve moderation system
  - [ ] Add warn system
  - [ ] Add action logging to user-configured channel
  - [ ] Add message delete/edit logging
- [ ] Add customizable welcome messages
- [ ] Add webpage with OAuth for users to change configuration, and other features
