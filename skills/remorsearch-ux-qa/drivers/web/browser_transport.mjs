// Launch locally or connect to a loopback Playwright launchServer endpoint.
import { DriverFailure } from './util.mjs';

const ENV = 'REMORSEARCH_BROWSER_WS';
// Extra Chromium switches for a local launch, space separated. A command sandbox that
// blocks Chromium's helper processes (Codex on macOS) can run it with --single-process.
const ARGS_ENV = 'REMORSEARCH_CHROMIUM_ARGS';

export function chromiumArgs(raw = process.env[ARGS_ENV]) {
  const args = (raw || '').split(/\s+/).filter(Boolean);
  for (const arg of args) {
    if (!/^--[a-z0-9][a-z0-9-]*(=[^\s]*)?$/.test(arg)) throw new DriverFailure(`${ARGS_ENV}: expected Chromium switches such as --single-process, got ${JSON.stringify(arg)}`);
  }
  return args;
}

export function validateBrowserWs(raw) {
  let url;
  try {
    url = new URL(raw);
  } catch {
    throw new DriverFailure(`${ENV}: expected a ws:// loopback URL`);
  }
  if (url.protocol !== 'ws:' || !['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname)
    || url.username || url.password || url.hash) {
    throw new DriverFailure(`${ENV}: only ws:// URLs on 127.0.0.1, localhost or [::1] without credentials or fragments are allowed`);
  }
  return url.href;
}

export async function openBrowser(pw, pwInfo, { headless = true, timeout = 60000, endpoint = process.env[ENV] } = {}) {
  const connected = endpoint !== undefined;
  const wsEndpoint = connected ? validateBrowserWs(endpoint) : null;
  let browser;
  try {
    // connect performs Playwright's client/server version handshake. This is the
    // Playwright protocol, not connectOverCDP and not a reused browser context.
    browser = connected ? await pw.chromium.connect(wsEndpoint, { timeout })
      : await pw.chromium.launch({ headless, timeout, args: chromiumArgs() });
  } catch (err) {
    const message = String(err.message);
    if (connected && /version mismatch/i.test(message)) {
      const server = message.match(/server version:\s*v([^\s|]+)/i)?.[1] || 'unknown';
      throw new DriverFailure(`${ENV}: Playwright client/server version mismatch (client ${pwInfo.version}, server ${server}); install the same Playwright version on both hosts`);
    }
    throw new DriverFailure(`${connected ? `${ENV}: cannot connect to the Playwright launchServer endpoint` : 'cannot launch Chromium'}: ${message.split('\n')[0]}`);
  }
  return {
    browser,
    connected,
    browserVersion: browser.version(),
    playwrightVersion: pwInfo.version,
    async close(contexts = []) {
      for (const context of contexts) if (context) await context.close().catch(() => {});
      // For BrowserType.connect, Browser.close disconnects this client. It never
      // invokes BrowserServer.close; other clients and their contexts survive.
      await browser.close().catch(() => {});
    },
  };
}
