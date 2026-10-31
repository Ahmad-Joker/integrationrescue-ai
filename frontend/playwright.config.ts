import { defineConfig } from '@playwright/test'

const isWin = process.platform === 'win32'
const python = process.env.IR_PYTHON ?? (isWin ? '..\\.venv\\Scripts\\python.exe' : '../.venv/bin/python')
const varDir = process.env.IR_E2E_VAR_DIR ?? '../var/e2e'

export default defineConfig({
  testDir: './e2e',
  timeout: 120_000,
  retries: 0,
  reporter: [['list']],
  use: { baseURL: 'http://127.0.0.1:5173', trace: 'retain-on-failure' },
  webServer: [
    {
      command: `${python} -m uvicorn integrationrescue.api:app --app-dir ../backend --host 127.0.0.1 --port 8000`,
      url: 'http://127.0.0.1:8000/api/health',
      env: { IR_VAR_DIR: varDir, IR_PROVIDER: 'deterministic' },
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1',
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
  ],
})
