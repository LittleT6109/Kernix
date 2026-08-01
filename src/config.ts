import { TOML } from 'bun';

interface Config {
  name: string;
  server: string;
  manager: string;
  trusted: string[];
  prod: boolean;
}

export const config = TOML.parse(
  await Bun.file(new URL('./config.toml', import.meta.url)).text()
) as Config;