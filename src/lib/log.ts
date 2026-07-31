function getTimestamp(): string {
  const now = new Date();

  return [
    now.getHours().toString().padStart(2, '0'),
    now.getMinutes().toString().padStart(2, '0'),
    now.getSeconds().toString().padStart(2, '0'),
  ].join(':');
}

export function logger(message: string): void {
  console.log(`[${getTimestamp()}] INFO: ${message}`);
}

logger.warn = function (message: string): void {
  console.log(`[${getTimestamp()}] WARN: ${message}`);
};

logger.error = function (message: string): void {
  console.log(`[${getTimestamp()}] ERROR: ${message}`);
};
