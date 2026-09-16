"use strict";

const assert = require("node:assert/strict");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");

const base = process.env.STUDY_BASE_URL || pathToFileURL(path.resolve(__dirname, "..") + path.sep).href;

async function open(page, chapter) {
  await page.goto(new URL(`ch${chapter}.html`, base).href);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(150);
  if (await page.locator("#onboardingSkip").isVisible()) await page.locator("#onboardingSkip").click();
}

async function checkSteps(player) {
  await player.locator('[data-action="reset"]').click();
  const range = player.locator('input[type="range"]');
  const last = Number(await range.getAttribute("max"));
  let height;
  for (let step = 0; step <= last; step += 1) {
    if (step) await player.locator('[data-action="next"]').click();
    assert.equal(Number(await range.inputValue()), step);
    const current = (await player.boundingBox()).height;
    if (height == null) height = current;
    assert.ok(Math.abs(height - current) < 1, `${await player.getAttribute("id")} changed height at step ${step}: ${height} -> ${current}`);
    const overflow = await player.locator(".study-detail").evaluate(el =>
      [...el.querySelectorAll(".study-search-detail > *, .study-clip-detail > *, [data-study-slot]")]
        .filter(node => node.scrollHeight > node.clientHeight + 1)
        .map(node => node.textContent.trim()));
    assert.deepEqual(overflow, [], `Explanation overflow at step ${step}`);
  }
  assert.ok(await player.locator('[data-action="next"]').isDisabled());
  await player.locator('[data-action="prev"]').click();
  assert.equal(Number(await range.inputValue()), last - 1);
  await player.locator('[data-action="reset"]').click();
  assert.equal(await range.inputValue(), "0");
  assert.ok(await player.locator('[data-action="prev"]').isDisabled());
  await range.focus();
  await range.press("ArrowRight");
  assert.equal(await range.inputValue(), "1");
  assert.ok(await range.evaluate(node => node === document.activeElement), "Range lost keyboard focus");
  await player.locator('[data-action="reset"]').click();
}

(async () => {
  const browser = await chromium.launch({ channel: process.env.CHROME_CHANNEL || "chrome", headless: true });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    let players = 0;
    for (const width of [320, 390, 768, 820, 1024, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      for (const chapter of [5, 6, 7, 8, 9, 10, 11, 12]) {
        await open(page, chapter);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `Horizontal overflow: ch${chapter} at ${width}`);
        for (const player of await page.locator(".study-player").all()) {
          await checkSteps(player);
          players += 1;
        }
        const first = page.locator(".study-player").first();
        await first.locator('[data-action="zoom"]').click();
        assert.ok(await page.locator("dialog[open]").isVisible());
        await page.keyboard.press("Escape");
        assert.equal(await page.locator("dialog[open]").count(), 0);
        assert.ok(await first.locator('[data-action="zoom"]').evaluate(node => node === document.activeElement));
      }
    }
    await page.setViewportSize({ width: 1440, height: 1000 });
    for (const chapter of [5, 6, 7, 8, 9, 10, 11, 12]) {
      await open(page, chapter);
      const player = page.locator(".study-player").first();
      const play = player.locator('[data-action="play"]');
      const range = player.locator("input");
      await play.scrollIntoViewIfNeeded();
      await page.waitForTimeout(500);
      const scroll = await page.evaluate(() => scrollY);
      await play.click();
      await page.waitForTimeout(1800);
      assert.equal(await range.inputValue(), "1");
      assert.ok(Math.abs(await page.evaluate(() => scrollY) - scroll) < 2, "Playback moved the page");
      await play.click();
      await page.waitForTimeout(1800);
      assert.equal(await range.inputValue(), "1", "Pause did not stop playback");
      await player.locator(".study-stops button").last().click();
      await play.click();
      assert.equal(await range.inputValue(), "0", "Replay did not start at the beginning");
      await play.click();
    }
    await open(page, 5);
    for (const key of ["bfs", "ucs", "greedy", "astar", "minimax", "dfs"]) {
      await page.locator(`#algorithmTabs [data-algorithm="${key}"]`).click();
      await checkSteps(page.locator("#studySearchLab .study-player"));
    }
    await open(page, 10);
    await page.locator('#labTabs [data-lab="clip"]').click();
    await checkSteps(page.locator("#labPanel .study-player"));
    await page.locator('#labPanel [data-action="play"]').click();
    await page.locator('#labTabs [data-lab="cnn"]').click();
    await page.waitForTimeout(1800);
    assert.equal(await page.locator('#labPanel [data-action="play"]').getAttribute("aria-pressed"), "false");
    for (const chapter of [6, 7, 8, 9, 10, 11, 12]) {
      await open(page, chapter);
      for (const tab of await page.locator("#labTabs [data-lab]").all()) {
        await tab.click();
        await checkSteps(page.locator("#labPanel .study-player"));
      }
    }
    await open(page, 11);
    const bellman = page.locator('.study-player').filter({ has: page.locator('[data-bellman-step]') }).first();
    await bellman.locator('[data-bellman-step="2"]').click();
    assert.equal(await bellman.locator('input').inputValue(), "2");
    await open(page, 12);
    const gan = page.locator('.study-player').filter({ has: page.locator('[data-gan-view]') }).first();
    await gan.locator('[data-gan-view="curve"]').click();
    await checkSteps(gan);
    assert.equal(await gan.locator('[data-gan-view="curve"]').getAttribute("aria-pressed"), "true");
    const painted = await gan.locator('canvas').evaluate(canvas => {
      const pixels = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
      let ink = 0;
      for (let i = 0; i < pixels.length; i += 4) if (pixels[i + 3] && pixels[i] < 220) ink++;
      return ink > 100;
    });
    assert.ok(painted, "GAN training chart is blank");
    await gan.locator('[data-action="zoom"]').click();
    await page.locator('dialog [data-gan-view="curve"]').click();
    assert.ok(await page.locator('dialog canvas').isVisible());
    await page.keyboard.press("Escape");
    await page.setViewportSize({ width: 390, height: 844 });
    await open(page, 7);
    const tree = page.locator('.study-player').first();
    await tree.evaluate(el => window.scrollTo(0, el.getBoundingClientRect().top + scrollY + 160));
    await page.waitForTimeout(200);
    const toolbar = await tree.locator('.study-toolbar').boundingBox();
    assert.ok(toolbar.y > 100 && toolbar.y < 240, "Mobile playback controls are not pinned below navigation");
    await open(page, 12);
    const diagram = page.locator('.study-viz-scroll').first();
    await diagram.focus();
    await diagram.press('ArrowRight');
    await page.waitForTimeout(300);
    assert.ok(await diagram.evaluate(el => el.scrollLeft > 0), "Diagram cannot be scrolled with the keyboard");
    assert.equal(await page.locator('.study-player input').first().inputValue(), "0", "Diagram scrolling changed the algorithm step");
    assert.deepEqual(errors, []);
    console.log(`PASS: ${players} responsive player runs across eight chapters; playback, focus, zoom and lab switching`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
