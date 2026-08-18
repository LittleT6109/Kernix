// A dead man's switch: it postpones a notification indefinitely.
// If the postpone loop stops, the notification goes through and alerts that the bot is down.
import { config } from '../config';
import { logger } from './log';

const { NTFY_CREDS } = process.env;

export function startDMSwitch(): void {
  setInterval(() => {
    fetch(config.ntfy_url, {
      method: 'POST',
      body: 'Warning: Kernix down!',
      headers: {
        In: '5m',
        Priority: '4',
        'X-Sequence-ID': 'heartbeat-check',
        Authorization: `Basic ${NTFY_CREDS}`, // Set NTFY_CREDS in your .env file
      },
    })
      .then(async (response) => {
        const body = await response.text();
        logger(
          `POST heartbeat-check -> ${response.status} ${response.statusText}: ${body}`
        );
      })
      .catch((error) => {
        logger.error(`POST heartbeat-check failed: ${error}`);
      });
  }, 60000); // Update every minute
}

export function cancelDMSwitch(): Promise<void> {
  return fetch(config.ntfy_url, {
    method: 'DELETE',
    headers: {
      'X-Sequence-ID': 'heartbeat-check',
      Authorization: `Basic ${NTFY_CREDS}`,
    },
  })
    .then(async (response) => {
      const body = await response.text();
      logger(
        `DELETE heartbeat-check -> ${response.status} ${response.statusText}: ${body}`
      );
    })
    .catch((error) => {
      logger.error(`Cancel failed: ${error}`);
    });
}
