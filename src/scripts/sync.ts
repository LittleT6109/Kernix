import { REST, Routes } from 'discord.js';
import { getSlashCommands } from '../utils/get-commands';

const { DISCORD_TOKEN, DISCORD_CLIENT_ID, DISCORD_GUILD_ID } = process.env;
if (!DISCORD_TOKEN || !DISCORD_CLIENT_ID || !DISCORD_GUILD_ID) {
  throw new Error(
    'Set DISCORD_TOKEN, DISCORD_CLIENT_ID, and DISCORD_GUILD_ID in .env.local'
  );
}

const commands = getSlashCommands();

console.log(`Syncing ${commands.length} command(s)...`);

const rest = new REST().setToken(DISCORD_TOKEN);

await rest.put(
  Routes.applicationGuildCommands(DISCORD_CLIENT_ID, DISCORD_GUILD_ID),
  { body: commands }
);

console.log(`Registered ${commands.length} command(s).`);
