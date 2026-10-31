import { expect, test } from '@playwright/test'

test('operator investigates, approves and sees an independently verified recovery', async ({ page }) => {
  const errors: string[] = []
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()))

  await page.goto('/#/new')
  await page.getByLabel('Seed').fill(String(Date.now() % 100000))
  await page.getByText('Duplicate webhook delivery').click()
  await page.getByRole('button', { name: 'Create and investigate' }).click()

  await expect(page).toHaveURL(/#\/incident\/inc_/)
  await expect(page.getByText('DETERMINISTIC MODE')).toBeVisible()
  await expect(page.getByText('awaiting approval').first()).toBeVisible({ timeout: 90_000 })
  await expect(page.getByText('FAIL (failure reproduced in isolation)', { exact: false })).toBeVisible()

  await page.getByRole('tab', { name: 'Repair' }).click()
  await expect(page.getByLabel('patch diff')).toContainText('price_plan_map')
  await page.getByLabel('approver').fill('e2e-reviewer')
  await page.getByRole('button', { name: 'Approve & promote' }).click()

  await page.getByRole('tab', { name: 'Verification' }).click()
  await expect(page.getByText('VERIFIED', { exact: true })).toBeVisible({ timeout: 60_000 })
  const row = page.getByRole('row', { name: /exactly_one_successful_charge/ }).first()
  await expect(row).toContainText('✓')

  await page.getByRole('tab', { name: 'Report' }).click()
  await expect(page.getByText('Independent verification', { exact: false })).toBeVisible()
  expect(errors).toEqual([])
})

test('ledger outage yields INDETERMINATE, never VERIFIED', async ({ page }) => {
  await page.goto('/#/new')
  await page.getByLabel('Seed').fill(String((Date.now() % 100000) + 1))
  await page.getByText('Billing ledger unavailable').click()
  await page.getByRole('button', { name: 'Create and investigate' }).click()
  const outcome = page.locator('.badge', { hasText: /^INDETERMINATE$/ })
  await expect(outcome.first()).toBeVisible({ timeout: 90_000 })
  await expect(page.locator('.badge', { hasText: /^VERIFIED$/ })).toHaveCount(0)
})
