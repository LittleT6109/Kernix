import {
  ChatInputCommandInteraction,
  GuildMember,
  SlashCommandBuilder,
  MessageFlags,
  ChannelType,
} from 'discord.js';
import { checkPermission } from '../../lib/permission';

export const slow = {
  data: new SlashCommandBuilder()
    .setName('slow')
    .setDescription('Sets the slowmode time')
    .addNumberOption((option) =>
      option
        .setName('value')
        .setDescription('Time to set the slowmode to in seconds')
        .setRequired(true)
        .setMinValue(0)
        .setMaxValue(21600)
    )
    .addStringOption((option) =>
      option
        .setName('reason')
        .setDescription('Reason for changing the slowmode')
        .setRequired(true)
    ),

  async execute(interaction: ChatInputCommandInteraction) {
    if (!interaction.inGuild()) {
      return interaction.reply({
        content: 'This command can only be used in a server.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const guild = interaction.guild;
    if (!guild) {
      return interaction.reply({
        content: 'This command can only be used in a server.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const member = interaction.member as GuildMember;
    const hasPermission = checkPermission(member, 'ManageChannels');
    if (!hasPermission) {
      return interaction.reply({
        content: 'You do not have permission to manage channels.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const channel = interaction.channel;
    const number = interaction.options.getNumber('value', true);
    const reason = interaction.options.getString('reason', true);

    if (channel?.type !== ChannelType.GuildText) {
      return interaction.reply({
        content: 'This is not a text channel.',
        flags: MessageFlags.Ephemeral,
      });
    }

    await channel.setRateLimitPerUser(number, reason);

    await interaction.reply(
      `${interaction.user.tag} set the slowmode time to "${number}" with reason "${reason}"`
    );
  },
};
