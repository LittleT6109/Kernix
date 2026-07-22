import { ping } from "../commands/utility/ping";

const commands = {
  ping,
  // TODO: Add more commands :P
} as const;

export function getCommands() {
  return Object.values(commands);
}

export function getSlashCommands() {
  return getCommands().map((command) => command.data.toJSON());
}
