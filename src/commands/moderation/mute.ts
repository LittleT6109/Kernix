import {
  ChatInputCommandInteraction,
  GuildMember,
  SlashCommandBuilder,
  MessageFlags,
} from 'discord.js';
import { checkPermission } from '../../lib/permission';
import { logger } from '../../lib/log';

export const mute = {
  data: new SlashCommandBuilder()
    .setName('mute')
    .setDescription('Mutes a member')
    .addUserOption((option) =>
      option
        .setName('user')
        .setDescription('The user to mute')
        .setRequired(true)
    )
    .addNumberOption((option) =>
      option
        .setName('time')
        .setDescription('The length of the mute in minutes')
        .setRequired(true)
    )
    .addStringOption((option) =>
      option
        .setName('reason')
        .setDescription('The reason for the mute')
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
    const hasPermission = checkPermission(member, 'ModerateMembers');
    if (!hasPermission) {
      return interaction.reply({
        content: 'You do not have permission to mute members.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const targetUser = interaction.options.getUser('user', true);
    const reason = interaction.options.getString('reason', true);

    if (targetUser.id === interaction.user.id) {
      return interaction.reply({
        content: 'You cannot mute yourself.',
        flags: MessageFlags.Ephemeral,
      });
    }

    if (targetUser.id === interaction.client.user?.id) {
      return interaction.reply({
        content: 'I cannot mute myself.',
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
        content: 'I do not have permission to mute that user.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const durationMinutes = interaction.options.getNumber('time', true);

    try {
      await targetUser.send(
        `You were muted in **${guild.name}** for ${durationMinutes} minutes by ${interaction.user.tag} with reason: "${reason}"`
      );
    } catch {}

    const muteTime = durationMinutes * 60_000;
    await targetMember.timeout(muteTime, reason);

    await interaction.reply(
      `${interaction.user.tag} muted ${targetUser.tag} for ${durationMinutes} minutes with reason: "${reason}"`
    );
    logger(
      `${interaction.user.username} muted ${targetUser.username} for ${durationMinutes} with reason: "${reason}"`
    );
  },
};

export const unmute = {
  data: new SlashCommandBuilder()
    .setName('unmute')
    .setDescription('Unutes a member')
    .addUserOption((option) =>
      option
        .setName('user')
        .setDescription('The user to unmute')
        .setRequired(true)
    )
    .addStringOption((option) =>
      option
        .setName('reason')
        .setDescription('The reason for unmuting')
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
    const hasPermission = checkPermission(member, 'ModerateMembers');
    if (!hasPermission) {
      return interaction.reply({
        content: 'You do not have permission to unmute members.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const targetUser = interaction.options.getUser('user', true);
    const reason = interaction.options.getString('reason', true);

    if (targetUser.id === interaction.user.id) {
      return interaction.reply({
        content: 'You cannot unmute yourself.',
        flags: MessageFlags.Ephemeral,
      });
    }

    if (targetUser.id === interaction.client.user?.id) {
      return interaction.reply({
        content: 'I am not muted.',
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
        content: 'I do not have permission to unmute that user.',
        flags: MessageFlags.Ephemeral,
      });
    }

    try {
      await targetUser.send(
        `You were unmuted in **${guild.name}** by ${interaction.user.tag} with reason: "${reason}"`
      );
    } catch {}

    await targetMember.timeout(null, reason);

    await interaction.reply(
      `${interaction.user.tag} unmuted ${targetUser.tag} with reason: "${reason}"`
    );
    logger(
      `${interaction.user.username} unmuted ${targetUser.username} with reason: "${reason}"`
    );
  },
};
