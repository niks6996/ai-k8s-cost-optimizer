const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-gpu']
  });

  const page = await browser.newPage({
    viewport: { width: 1600, height: 1100 },
    deviceScaleFactor: 1
  });

  page.on('console', msg => console.log(`BROWSER: ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`PAGE ERROR: ${err.message}`));

  const url =
    'http://127.0.0.1:3000/d/optimizer-dashboard/ai-kubernetes-cost-performance-optimizer' +
    '?orgId=1&from=now-15m&to=now&refresh=5s&kiosk';

  await page.goto(url, {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });

  // Grafana's frontend loads asynchronously. Wait for a real dashboard panel,
  // rather than relying on networkidle.
  await page.waitForSelector(
    '[data-testid="data-testid Panel header Workloads Analysed"], .panel-title, [data-testid^="data-testid Panel header"]',
    { timeout: 60000 }
  );

  await page.waitForTimeout(10000);

  const bodyText = await page.locator('body').innerText();
  if (bodyText.includes('Grafana has failed to load its application files')) {
    throw new Error('Grafana frontend assets failed to load');
  }

  await page.screenshot({
    path: 'monitoring-evidence/grafana-dashboard.png',
    fullPage: true
  });

  console.log('Grafana dashboard screenshot captured successfully.');
  await browser.close();
})();