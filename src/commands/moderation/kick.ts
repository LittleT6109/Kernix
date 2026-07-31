import {
  ChatInputCommandInteraction,
  GuildMember,
  SlashCommandBuilder,
  MessageFlags,
} from 'discord.js';
import { checkPermission } from '../../lib/permission';
import { logger } from '../../lib/log';

export const kick = {
  data: new SlashCommandBuilder()
    .setName('kick')
    .setDescription('Kicks a member')
    .addUserOption((option) =>
      option
        .setName('user')
        .setDescription('The user to kick')
        .setRequired(true)
    )
    .addStringOption((option) =>
      option
        .setName('reason')
        .setDescription('The reason for the kick')
        .setRequired(true)
        .setMaxLength(512)
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
    const hasPermission = checkPermission(member, 'KickMembers');
    if (!hasPermission) {
      return interaction.reply({
        content: 'You do not have permission to kick members.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const targetUser = interaction.options.getUser('user', true);
    const reason = interaction.options.getString('reason', true);

    if (targetUser.id === interaction.user.id) {
      return interaction.reply({
        content: 'You cannot kick yourself.',
        flags: MessageFlags.Ephemeral,
      });
    }

    if (targetUser.id === interaction.client.user?.id) {
      return interaction.reply({
        content: 'I cannot kick myself.',
        flags: MessageFlags.Ephemeral,
      });
    }

    if (guild.ownerId === targetUser.id) {
      return interaction.reply({
        content: 'You cannot kick the server owner.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const targetMember = await guild.members
      .fetch(targetUser.id)
      .catch(() => null);
    if (!targetMember) {
      return interaction.reply({
        content: 'That user is not in this server.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const botMember = guild.members.me ?? (await guild.members.fetchMe());
    if (
      targetMember.roles.highest.comparePositionTo(botMember.roles.highest) > 0
    ) {
      return interaction.reply({
        content: 'I do not have permission to kick that user.',
        flags: MessageFlags.Ephemeral,
      });
    }

    try {
      await targetUser.send(
        `You were kicked from **${guild.name}** by ${interaction.user.tag} with reason: "${reason}"`
      );
    } catch {}

    await guild.members.kick(targetUser.id, reason);

    await interaction.reply(
      `${interaction.user.tag} kicked ${targetUser.tag} with reason: "${reason}"`
    );
    logger(
      `${interaction.user.username} kicked ${targetUser.username} with reason: "${reason}"`
    );
  },
};
