import {
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  MessageFlags,
  ChannelType,
  TextChannel,
} from 'discord.js';
import { config } from '../../config';

const profanityListUrl =
  'https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en';

let profanityPatternsPromise: Promise<RegExp[]> | null = null;

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function getProfanityPatterns() {
  if (!profanityPatternsPromise) {
    profanityPatternsPromise = fetch(profanityListUrl)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load profanity list: ${response.status}`);
        }

        return response.text();
      })
      .then((body) =>
        body
          .split('\n')
          .map((line) => line.trim())
          .filter((line) => line.length > 0 && !line.startsWith('#'))
          .map((term) => new RegExp(`\\b${escapeRegExp(term)}\\b`, 'i'))
      );
  }

  return profanityPatternsPromise;
}

function removeMassMentions(text: string) {
  return text.replace(/@(everyone|here)\b/gi, '@\u200b$1');
}

export const message = {
  data: new SlashCommandBuilder()
    .setName('message')
    .setDescription('Send a message as the bot')
    .addStringOption((option) =>
      option
        .setName('text')
        .setDescription('The message to send')
        .setRequired(true)
    )
    .addChannelOption((option) =>
      option
        .setName('channel')
        .setDescription('The channel to send the message in')
        .addChannelTypes(ChannelType.GuildText)
        .setRequired(false)
    ),

  async execute(interaction: ChatInputCommandInteraction) {
    if (
      interaction.user.id !== config.manager &&
      !config.trusted.includes(interaction.user.id)
    ) {
      return interaction.reply({
        content: 'You do not have permission to run this command.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const text = interaction.options.getString('text', true);
    const channel = (interaction.options.getChannel('channel') ??
      interaction.channel) as TextChannel;

    if (!channel?.isSendable()) {
      return interaction.reply({
        content: 'I cannot send messages in this channel.',
        flags: MessageFlags.Ephemeral,
      });
    }

    let profanityPatterns: RegExp[];
    try {
      profanityPatterns = await getProfanityPatterns();
    } catch {
      return interaction.reply({
        content: 'I could not load the profanity filter right now.',
        flags: MessageFlags.Ephemeral,
      });
    }

    if (profanityPatterns.some((pattern) => pattern.test(text))) {
      return interaction.reply({
        content: 'That message contains profanity and cannot be sent.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const sanitizedText = removeMassMentions(text);

    await channel.send(sanitizedText);

    return interaction.reply({
      content: 'Message sent.',
      flags: MessageFlags.Ephemeral,
    });
  },
};
