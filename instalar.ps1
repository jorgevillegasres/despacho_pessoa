# Instalador del Despacho Pessoa para Windows.
# No lo abras con doble clic: usa instalar.cmd, que lo ejecuta con los permisos correctos.
# Opciones para pruebas: -Simular (no instala nada), -Herramienta claude|opencode|codex|ninguna, -SinPreguntas
param(
    [switch]$Simular,
    [ValidateSet('', 'claude', 'opencode', 'codex', 'ninguna')]
    [string]$Herramienta = '',
    [switch]$SinPreguntas
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }  # el modo restringido de Windows no lo permite; solo afecta a los acentos
Set-Location -LiteralPath $PSScriptRoot
$Ayuda = 'docs\guias\problemas-frecuentes.md'
$ClaudeMinima = [version]'2.1.295'  # desde esta versión los controles (hooks) bloquean siempre
$Herramientas = @{
    claude   = @{ Nombre = 'Claude Code'; Npm = '@anthropic-ai/claude-code'; Comando = 'claude';   Guia = 'nivel-2-claude-code.md'
                  Primero = '@01-observador-caeiro Lee casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribe casos/mi-primer-caso/02-hechos/hechos.md según tu contrato de salida.' }
    opencode = @{ Nombre = 'OpenCode';    Npm = 'opencode-ai';               Comando = 'opencode'; Guia = 'nivel-2-opencode.md'
                  Primero = '@01-observador-caeiro Lee casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribe casos/mi-primer-caso/02-hechos/hechos.md según tu contrato de salida.' }
    codex    = @{ Nombre = 'Codex';       Npm = '@openai/codex';             Comando = 'codex';    Guia = 'nivel-2-codex.md'
                  Primero = 'Usa el agente 01-observador-caeiro para leer casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribir casos/mi-primer-caso/02-hechos/hechos.md según su contrato de salida.' }
}

function Paso([int]$n, [string]$texto) { Write-Host ''; Write-Host "[$n/4] $texto" -ForegroundColor Cyan }
function Bien([string]$texto) { Write-Host "  ✔ $texto" -ForegroundColor Green }
function Donde-Ayuda([string]$ancla) {
    # $ancla llega como '#python'.
    Write-Host "  Qué hacer: abre el archivo $Ayuda de esta carpeta, sección $ancla."
}
function Falla([string]$texto, [string]$ancla) {
    Write-Host "  ✘ $texto" -ForegroundColor Red
    Donde-Ayuda $ancla
    exit 1
}
function Aviso([string]$texto, [string]$ancla) {
    Write-Host "  ! $texto" -ForegroundColor Yellow
    Donde-Ayuda $ancla
}
function Tiene([string]$comando) { [bool](Get-Command $comando -ErrorAction SilentlyContinue) }
function Refrescar-Ruta {
    $env:Path = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment').Path + ';' + (Get-ItemProperty HKCU:\Environment -ErrorAction SilentlyContinue).Path
}
function Buscar-Python {
    # Devuelve @{ Exe; Args } de un Python >= 3.10 que de verdad responda (no el atajo de la Microsoft Store).
    foreach ($c in @(@{ Exe = 'python'; Args = @() }, @{ Exe = 'py'; Args = @('-3') })) {
        if (-not (Tiene $c.Exe)) { continue }
        try { $v = & $c.Exe @($c.Args) -c 'import sys; print(int(sys.version_info >= (3, 10)))' 2>$null } catch { continue }
        if ("$v".Trim() -eq '1') { return $c }
    }
    return $null
}
function Instalar-Winget([string]$id, [string]$nombre, [string]$ancla) {
    if ($Simular) { Write-Host "  (simulación) winget install --id $id"; return }
    if (-not (Tiene 'winget')) { Falla "No encontré winget para instalar $nombre." $ancla }
    Write-Host "  Instalando $nombre con winget (puede tardar unos minutos)..."
    winget install --id $id -e --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) { Falla "winget no pudo instalar $nombre." $ancla }
    Refrescar-Ruta
}
function Version-Claude {
    # Devuelve la versión instalada de Claude Code como [version], o $null si no se pudo leer.
    $exe = if (Tiene 'claude.cmd') { 'claude.cmd' } else { 'claude' }
    try {
        $salida = (& $exe --version 2>&1 | Out-String)
        $m = [regex]::Match($salida, '\d+\.\d+\.\d+')
        if ($m.Success) { return [version]$m.Value }
    } catch { }
    return $null
}

Write-Host 'Instalador del Despacho Pessoa' -ForegroundColor Cyan
Write-Host 'Voy a comprobar Python, instalar la herramienta que elijas y probar que todo funciona.'
if (-not $SinPreguntas) {
    $r = Read-Host '¿Continuar? (S/n)'
    if ($r -and $r -notmatch '^[sSyY]') { Write-Host 'No hice nada. Hasta pronto.'; exit 0 }
}

Paso 1 'Python 3 (lo usan la calculadora de plazos y los validadores)'
$Py = Buscar-Python
if (-not $Py) {
    Instalar-Winget 'Python.Python.3.13' 'Python 3' '#python'
    $Py = Buscar-Python
}
if ($Py) { Bien "Python listo ($($Py.Exe))." }
elseif ($Simular) { Write-Host '  (simulación) Python no disponible: en una instalación real aquí se instalaría y se volvería a comprobar.' }
else { Falla 'Python 3 no quedó disponible. Cierra esta ventana y vuelve a hacer doble clic en instalar.cmd.' '#python' }

Paso 2 'La herramienta'
if (-not $Herramienta) {
    if ($SinPreguntas) { $Herramienta = 'ninguna' }
    else {
        Write-Host '  ¿Con qué herramienta quieres trabajar?'
        Write-Host '    1. Claude Code    2. OpenCode    3. Codex    4. Aún no sé (no instalo ninguna)'
        $opcion = (Read-Host '  Escribe el número').Trim()
        $Herramienta = @{ '1' = 'claude'; '2' = 'opencode'; '3' = 'codex' }[$opcion]
        if (-not $Herramienta) { $Herramienta = 'ninguna' }
    }
}
if ($Herramienta -eq 'ninguna') {
    Write-Host '  No instalo ninguna. Puedes volver a ejecutar el instalador cuando decidas.'
} else {
    $h = $Herramientas[$Herramienta]
    if (Tiene 'node') { Bien "Node listo ($(node --version))." }
    else {
        Instalar-Winget 'OpenJS.NodeJS.LTS' 'Node' '#node'
        if (-not $Simular -and -not (Tiene 'node')) { Falla 'Node no quedó disponible. Cierra esta ventana y vuelve a abrir instalar.cmd.' '#node' }
    }
    if ($Herramienta -eq 'claude' -and -not (Tiene 'git')) { Instalar-Winget 'Git.Git' 'Git for Windows' '#git' }
    if (Tiene $h.Comando) {
        Bien "$($h.Nombre) ya está instalado."
        if ($Herramienta -eq 'claude') {
            $v = Version-Claude
            if ($v -and $v -lt $ClaudeMinima) {
                Aviso "Tu Claude Code es la versión $v; el despacho necesita $ClaudeMinima o posterior para que los controles bloqueen siempre. Actualiza con: npm install -g @anthropic-ai/claude-code@latest" '#confianza-carpeta'
            }
        }
    }
    elseif ($Simular) { Write-Host "  (simulación) npm install -g $($h.Npm)" }
    else {
        Write-Host "  Instalando $($h.Nombre) (npm install -g $($h.Npm))..."
        & npm.cmd install -g $h.Npm
        if ($LASTEXITCODE -ne 0) { Falla "npm no pudo instalar $($h.Nombre)." '#instalar-herramienta' }
        Refrescar-Ruta
        Bien "$($h.Nombre) instalado."
    }
}

Paso 3 'Compruebo que el despacho funciona'
if (-not $Py) {
    Write-Host '  (simulación) se omite la comprobación: no hay Python con el que correrla.'
} else {
    & $Py.Exe @($Py.Args) herramientas\verificar_corpus.py --comprobar
    if ($LASTEXITCODE -ne 0) { Falla 'El corpus de fuentes/ no coincide con su sello.' '#verificacion' }
    & $Py.Exe @($Py.Args) herramientas\calcular_plazos.py --demo-casos | Out-Null
    if ($LASTEXITCODE -ne 0) { Falla 'La calculadora de plazos no corrió.' '#verificacion' }
    Bien 'Corpus intacto y calculadora funcionando.'
}

Paso 4 'Listo'
if ($Herramienta -eq 'ninguna') {
    Write-Host '  Puedes usar el despacho en el chat: abre docs\guias\nivel-1-chat.md.'
} else {
    $h = $Herramientas[$Herramienta]
    Write-Host "  1. Abre una terminal en esta carpeta: $PSScriptRoot"
    Write-Host '     (en el Explorador de archivos, clic derecho dentro de la carpeta > Abrir en Terminal)'
    $orden = if (Tiene "$($h.Comando).cmd") { "$($h.Comando).cmd" } else { $h.Comando }
    Write-Host "  2. Escribe: $orden"
    if ($Herramienta -eq 'opencode') { Write-Host '  3. Escribe:' }
    else { Write-Host '  3. Cuando pregunte si confías en la carpeta, responde que sí. Luego escribe:' }
    Write-Host "     $($h.Primero)"
    Write-Host "  Guía paso a paso: docs\guias\$($h.Guia)"
}
exit 0
