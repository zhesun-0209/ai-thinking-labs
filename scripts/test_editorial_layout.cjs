"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const { chromium } = require("playwright");
const base = process.env.STUDY_BASE_URL || "http://127.0.0.1:8772/";
const output = process.env.STUDY_SCREENSHOTS || "/tmp/shapeofai-editorial-review";

(async () => {
  await fs.mkdir(output, { recursive: true });
  const browser = await chromium.launch({ channel: "chrome", headless: true });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    for (const width of [320, 390, 820, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      for (let chapter = 5; chapter <= 12; chapter++) {
        await page.goto(new URL(`ch${chapter}.html`, base).href);
        await page.evaluate(() => document.fonts.ready);
        if (await page.locator("#onboardingSkip").isVisible()) await page.locator("#onboardingSkip").click();
        assert.equal(await page.locator(".study-section-number").count(), await page.locator(".chapter-section > .section-header h2").count());
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
        for (const label of await page.locator('.cell-header').all()) {
          if (["要点", "演示"].includes((await label.locator('.cell-label').textContent()).trim())) assert.equal(await label.isVisible(), false);
        }
        const resources = page.locator('.study-resources').first();
        assert.ok(await resources.count(), `No practice disclosure in chapter ${chapter}`);
        assert.equal(await resources.locator('button').first().isVisible(), false);
        await resources.locator('summary').click();
        assert.ok(await resources.locator('button').first().isVisible());
        await resources.locator('summary').click();
        for (const button of await page.locator('.study-actions button').all()) {
          assert.ok(await button.getAttribute('aria-label'));
          assert.equal(await button.locator('svg').count(), 1);
        }
        if (chapter === 12) {
          const mcts = page.locator('.study-player').filter({has: page.locator('.mcts-svg')}).first();
          for (let step = 0; step < 4; step++) {
            if (step) await mcts.locator('[data-action="next"]').click();
            const bounds = await mcts.locator('.mcts-svg').evaluate(svg => {
              const box = svg.getBoundingClientRect();
              return [...svg.querySelectorAll('.mcts-node-box')].every(node => {
                const n = node.getBoundingClientRect();
                return n.left >= box.left && n.right <= box.right && n.top >= box.top && n.bottom <= box.bottom;
              });
            });
            assert.ok(bounds, `MCTS node clipped at width ${width}, step ${step}`);
            assert.equal(await mcts.locator('.study-viz-scroll').evaluate(el => el.scrollWidth > el.clientWidth + 1), false);
          }
          await mcts.locator('[data-action="reset"]').click();
          assert.match(await mcts.locator('.study-detail').textContent(), /1.38[\s\S]*1.57/);
          await mcts.evaluate(el => el.scrollIntoView({block: 'start'}));
          await page.waitForTimeout(250);
          await page.screenshot({path: `${output}/mcts-${width}.png`});
        }
        if (chapter === 10) {
          const mae = page.locator('.study-player').filter({has: page.locator('.mae-study')}).first();
          const original = await mae.locator('[data-mae-original]').innerHTML();
          for (let step = 1; step < 4; step++) {
            await mae.locator('[data-action="next"]').click();
            assert.equal(await mae.locator('[data-mae-original]').innerHTML(), original, 'MAE original changed');
            assert.equal(await mae.locator('[data-mae-current] .is-masked').count(), step < 3 ? 3 : 0);
          }
          assert.equal(await mae.locator('[data-mae-current] .is-recon').count(), 3);
          await mae.evaluate(el => el.scrollIntoView({block: 'start'}));
          await page.waitForTimeout(250);
          await page.screenshot({path: `${output}/mae-${width}.png`});
        }
        await page.evaluate(() => scrollTo(0, 0));
        await page.waitForTimeout(200);
        assert.equal(await page.locator('.section-link.is-active[data-section]').getAttribute('data-section'), 'hero');
        await page.screenshot({path: `${output}/ch${chapter}-${width}.png`});
      }
    }
    await page.goto(new URL('hub.html', base).href);
    const input = page.locator('input[type="search"]');
    await input.fill('注意力');
    assert.ok(await page.locator('.hub-card:visible').count() > 0);
    await input.fill('不存在的案例XYZ');
    assert.equal(await page.locator('.hub-card:visible').count(), 0);
    await input.fill('');
    assert.equal(await page.locator('.hub-card:visible').count(), 8);
    await page.screenshot({path: `${output}/hub-1440.png`});
    assert.deepEqual(errors, []);
    console.log('PASS: 32 chapter/viewport combinations, accessible icons, practice disclosures, MCTS visibility, MAE state separation and hub search');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
