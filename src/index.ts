import { Client, Events, GatewayIntentBits } from 'discord.js';
import { logger } from './lib/log';
import { getCommands } from './utils/get-commands';
import { syncCommands } from './lib/sync';

syncCommands();

const { DISCORD_TOKEN } = process.env;
if (!DISCORD_TOKEN) {
  throw new Error('Set DISCORD_TOKEN in .env.local');
}

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.once(Events.ClientReady, (readyClient) => {
  logger(`Logged in as ${readyClient.user.tag}`);
});

client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const command = getCommands().find(
    (entry) => entry.data.name === interaction.commandName
  );

  if (!command) {
    await interaction.reply({
      content: 'That command does not exist.',
      ephemeral: true,
    });
    logger.warn(`${interaction.user.username} tried to run command "/${interaction.commandName}", but it does not exist.`)
    return;
  }

  await command.execute(interaction);
});

client.login(DISCORD_TOKEN);
