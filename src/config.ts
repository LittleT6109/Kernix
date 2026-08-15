import { TOML } from 'bun';
import { existsSync } from 'node:fs';
import { copyFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

interface Config {
  name: string;
  server: string;
  manager: string;
  trusted: string[];
  prod: boolean;
}

const configUrl = new URL('./data/config.toml', import.meta.url);
const defaultUrl = new URL('./defaults/config.toml', import.meta.url);
const configPath = fileURLToPath(configUrl);
const defaultPath = fileURLToPath(defaultUrl);

if (!existsSync(configPath)) {
  await mkdir(dirname(configPath), { recursive: true });
  await copyFile(defaultPath, configPath);
}

export const config = TOML.parse(await Bun.file(configPath).text()) as Config;
