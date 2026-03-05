$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Ensure-Dir($path) { if (!(Test-Path $path)) { New-Item -ItemType Directory -Path $path -Force | Out-Null } }
function Write-File($path, $content) {
  $dir = Split-Path $path -Parent
  if ($dir -and !(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  Set-Content -Path $path -Value $content -Encoding UTF8
}

Write-Info "Criando estrutura do BoxRota..."

$dirs = @(
  "backend/app/api/routes",
  "backend/app/core",
  "backend/app/db",
  "backend/app/models",
  "backend/app/schemas",
  "backend/app/services",
  "backend/app/utils",
  "backend/alembic/versions",
  "frontend/public",
  "frontend/src/assets",
  "frontend/src/components",
  "frontend/src/components/layout",
  "frontend/src/components/ui",
  "frontend/src/context",
  "frontend/src/hooks",
  "frontend/src/lib",
  "frontend/src/pages",
  "frontend/src/pages/app",
  "frontend/src/pages/auth",
  "frontend/src/pages/public",
  "frontend/src/router",
  "frontend/src/styles"
)

foreach ($d in $dirs) { Ensure-Dir $d }

Write-Info "Escrevendo arquivos base..."

Write-File "README.md" @"
# BoxRota
Retorno automático. Oficina organizada.

## Stack
- Backend: FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, JWT (access + refresh), RBAC, Multi-tenant (workshop_id)
- Frontend: React + TypeScript (Vite), React Router, Mobile-first

## Rodar (quando pronto)
Veja instruções finais no último passo do processo.
"@

Write-File ".gitignore" @"
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
.venv/
venv/
.env
.env.*

node_modules/
dist/
.vite/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*

.DS_Store
.idea/
.vscode/
"@

Write-File "backend/app/__init__.py" ""
Write-File "backend/app/api/routes/__init__.py" ""
Write-File "backend/app/models/__init__.py" ""
Write-File "backend/app/schemas/__init__.py" ""
Write-File "backend/app/services/__init__.py" ""
Write-File "backend/app/utils/__init__.py" ""

Write-Info "Estrutura criada com sucesso."