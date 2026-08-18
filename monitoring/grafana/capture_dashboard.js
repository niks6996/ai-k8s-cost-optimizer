const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });

  const page = await browser.newPage({
    viewport: { width: 1600, height: 1100 }
  });

  await page.goto(
    'http://127.0.0.1:3000/d/optimizer-dashboard/ai-kubernetes-cost-performance-optimizer?orgId=1&from=now-15m&to=now&kiosk',
    {
      waitUntil: 'networkidle',
      timeout: 60000
    }
  );

  await page.waitForTimeout(10000);

  await page.screenshot({
    path: 'monitoring-evidence/grafana-dashboard.png',
    fullPage: true
  });

  await browser.close();
})();