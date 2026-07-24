import type { GuildMember, PermissionResolvable } from 'discord.js';

export function checkPermission(
  member: GuildMember,
  permission: PermissionResolvable
): boolean {
  return member.permissions.has(permission);
}
