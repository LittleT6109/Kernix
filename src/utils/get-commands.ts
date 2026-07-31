import { ping } from '../commands/utility/ping';
import { ban, unban } from '../commands/moderation/ban';
import { kick } from '../commands/moderation/kick';
import { mute, unmute } from '../commands/moderation/mute';
import { slow } from '../commands/moderation/slow';
import { message } from '../commands/fun/message';

const commands = {
  // moderation
  ban,
  unban,
  kick,
  mute,
  unmute,
  slow,
  // utility
  ping,
  //fun
  message
  // TODO: Add more commands :P
} as const;

export function getCommands() {
  return Object.values(commands);
}

export function getSlashCommands() {
  return getCommands().map((command) => command.data.toJSON());
}
