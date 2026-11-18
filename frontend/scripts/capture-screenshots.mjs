// Capture deck screenshots from a running judge-demo server (fictional data only).
//
//   $env:IR_ACCESS_TOKEN = "<access code of that server>"
//   node frontend/scripts/capture-screenshots.mjs --url http://127.0.0.1:8080 --out competition/screenshots
//
// Runs one real incident with the provider given by --provider (default gemini: spends about 12-20 free-tier
// requests), approves it as "Demo reviewer", and saves element-level PNGs (no browser chrome). The access code is
// injected into sessionStorage, so it never appears on screen.
import { chromium } from '@playwright/test'
import { mkdirSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`)
  return i > 0 ? process.argv[i + 1] : fallback
}
const BASE = arg('url', 'http://127.0.0.1:8080')
const OUT = arg('out', 'competition/screenshots')
const PROVIDER = arg('provider', 'gemini')
const TOKEN = process.env.IR_ACCESS_TOKEN ?? ''
mkdirSync(OUT, { recursive: true })

const browser = await chromium.launch()
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, colorScheme: 'dark' })
await ctx.addInitScript((code) => sessionStorage.setItem('ir_access_code', code), TOKEN)
const page = await ctx.newPage()
const shots = []
const shot = async (name, locator) => {
  const file = join(OUT, `${name}.png`)
  await (locator ?? page).screenshot({ path: file, ...(locator ? {} : { fullPage: false }) })
  shots.push(name)
  console.log('saved', file)
}
const panel = (title) => page.locator('.panel', { has: page.locator('h2', { hasText: title }) }).first()

// 1. Dashboard (seeded baseline examples + recorded evaluation)
await page.goto(`${BASE}/#/`)
await page.getByText('Total incidents').waitFor()
await page.waitForTimeout(1500)
await shot('01_dashboard')

// 2. New incident with the featured preset and live Gemini selected
await page.goto(`${BASE}/#/new`)
await page.getByRole('button', { name: /Paid for Pro, still on Free/ }).click()
await page.getByLabel('Seed').fill(String(Date.now() % 100000))
if (PROVIDER !== 'deterministic') await page.getByLabel('Decision maker').selectOption(PROVIDER)
await page.waitForTimeout(500)
await shot('02_new_incident')

// 3. Run it
await page.getByRole('button', { name: 'Create and investigate' }).click()
await page.waitForURL(/#\/incident\/inc_/)
const id = page.url().split('/').pop()
await page.locator('.mode-banner').first().waitFor()
await shot('03_mode_banner', page.locator('.mode-banner').first())
await page.getByText('awaiting approval').first().waitFor({ timeout: 480_000 })
await page.waitForTimeout(1000)
await shot('04_incident_overview')
await shot('05_tool_timeline', panel('Tool calls'))
await shot('06_hypotheses', panel('Hypotheses'))
await shot('07_root_cause_reproduced', panel('Root cause'))

// 4. Repair evidence and the human gate
await page.getByRole('tab', { name: 'Repair' }).click()
const accepted = page.locator('.panel', { has: page.locator('.badge', { hasText: 'accepted' }) }).first()
await accepted.waitFor()
await shot('08_repair_diff_tests', accepted)
await shot('09_approval_gate', panel('Human approval required'))
await page.getByLabel('approver').fill('Demo reviewer')
await page.getByRole('button', { name: 'Approve & promote' }).click()

// 5. Independent verification
await page.getByRole('tab', { name: 'Verification' }).click()
await page.locator('.badge', { hasText: /^VERIFIED$/ }).first().waitFor({ timeout: 180_000 })
await page.waitForTimeout(1000)
await shot('10_verification_after', panel('Environment after promotion'))
await shot('11_reproduction_before', panel('Reproduction (unpatched)'))
await shot('12_verified_overview')

// 6. Evaluation lab: live Gemini vs baseline
await page.goto(`${BASE}/#/eval`)
await page.getByRole('tab', { name: /Live gemini .* 11 runs/ }).click()
await page.waitForTimeout(800)
await shot('13_eval_live_gemini')
await page.getByRole('tab', { name: /Baseline .* 22 runs/ }).click()
await page.waitForTimeout(800)
await shot('14_eval_baseline')

const inc = await (await page.request.get(`${BASE}/api/incidents/${id}`)).json()
writeFileSync(join(OUT, 'capture.json'), JSON.stringify({
  captured_at: new Date().toISOString(), incident: id, provider: inc.provider, mode: inc.mode,
  outcome: inc.outcome, usage: inc.usage, tool_calls: inc.trace.length, shots,
}, null, 2) + '\n')
console.log(`incident ${id}: ${inc.mode} ${inc.provider} -> ${inc.outcome}`)
await browser.close()
