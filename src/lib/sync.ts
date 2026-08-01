import { REST, Routes } from 'discord.js';
import { getSlashCommands } from '../utils/get-commands';
import { config } from '../config';
import { logger } from './log';

export async function syncCommands() {
  const { DISCORD_TOKEN, DISCORD_CLIENT_ID } = process.env;
  const DISCORD_GUILD_ID = config.server;

  if (!DISCORD_TOKEN || !DISCORD_CLIENT_ID) {
    throw new Error('Set DISCORD_TOKEN and DISCORD_CLIENT_ID in .env.local');
  }

  const commands = getSlashCommands();
  const rest = new REST().setToken(DISCORD_TOKEN);

  const prod = config.prod;

  if (!prod) {
    if (!DISCORD_GUILD_ID) {
      throw new Error("Set 'server' in config.toml");
    }

    logger(`Syncing ${commands.length} command(s) to ${DISCORD_GUILD_ID}...`);
    await rest.put(
      Routes.applicationGuildCommands(DISCORD_CLIENT_ID, DISCORD_GUILD_ID),
      { body: commands }
    );
  } else {
    logger(`Syncing ${commands.length} command(s) to the global cache...`);
    await rest.put(Routes.applicationCommands(DISCORD_CLIENT_ID), {
      body: commands,
    });
  }

  logger(`Registered ${commands.length} command(s).`);
}
