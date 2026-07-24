import {
  ChatInputCommandInteraction,
  GuildMember,
  SlashCommandBuilder,
  MessageFlags,
} from 'discord.js';
import { checkPermission } from '../../lib/permission';

export const ban = {
  data: new SlashCommandBuilder()
    .setName('ban')
    .setDescription('Bans a member')
    .addUserOption((option) =>
      option.setName('user').setDescription('The user to ban').setRequired(true)
    )
    .addStringOption((option) =>
      option
        .setName('reason')
        .setDescription('The reason for the ban')
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
    const hasPermission = checkPermission(member, 'BanMembers');
    if (!hasPermission) {
      return interaction.reply({
        content: 'You do not have permission to ban members.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const targetUser = interaction.options.getUser('user', true);
    const reason = interaction.options.getString('reason', true);

    if (targetUser.id === interaction.user.id) {
      return interaction.reply({
        content: 'You cannot ban yourself.',
        flags: MessageFlags.Ephemeral,
      });
    }

    if (targetUser.id === interaction.client.user?.id) {
      return interaction.reply({
        content: 'I cannot ban myself.',
        flags: MessageFlags.Ephemeral,
      });
    }

    if (guild.ownerId === targetUser.id) {
      return interaction.reply({
        content: 'You cannot ban the server owner.',
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
        content: 'I do not have permission to ban that user.',
        flags: MessageFlags.Ephemeral,
      });
    }

    try {
      await targetUser.send(
        `You were banned from **${guild.name}** by ${interaction.user.tag} with reason: "${reason}"`
      );
    } catch {}

    await guild.members.ban(targetUser.id, { reason });

    await interaction.reply(
      `${interaction.user.tag} banned ${targetUser.tag} with reason: "${reason}"`
    );
  },
};

export const unban = {
  data: new SlashCommandBuilder()
    .setName('unban')
    .setDescription('Unbans a member')
    .addStringOption((option) =>
      option
        .setName('user')
        .setDescription('The user ID to unban')
        .setRequired(true)
    )
    .addStringOption((option) =>
      option
        .setName('reason')
        .setDescription('The reason for unbanning')
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
    const hasPermission = checkPermission(member, 'BanMembers');
    if (!hasPermission) {
      return interaction.reply({
        content: 'You do not have permission to unban members.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const targetUserId = interaction.options.getString('user', true).trim();
    const reason = interaction.options.getString('reason', true);

    if (!/^\d{17,20}$/.test(targetUserId)) {
      return interaction.reply({
        content: 'Please provide a valid user ID.',
        flags: MessageFlags.Ephemeral,
      });
    }

    if (targetUserId === interaction.user.id) {
      return interaction.reply({
        content: 'You cannot unban yourself, because you are not banned.',
        flags: MessageFlags.Ephemeral,
      });
    }

    if (targetUserId === interaction.client.user?.id) {
      return interaction.reply({
        content: 'I cannot unban myself, because I am not banned.',
        flags: MessageFlags.Ephemeral,
      });
    }

    if (guild.ownerId === targetUserId) {
      return interaction.reply({
        content:
          'You cannot unban the server owner, because they are not banned.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const banEntry = await guild.bans.fetch(targetUserId).catch(() => null);
    if (!banEntry) {
      return interaction.reply({
        content: 'That user is not currently banned.',
        flags: MessageFlags.Ephemeral,
      });
    }

    const targetUser = banEntry.user;

    await guild.members.unban(targetUser.id, reason);

    await interaction.reply(
      `${interaction.user.tag} unbanned ${targetUser.tag} with reason: "${reason}"`
    );
  },
};
