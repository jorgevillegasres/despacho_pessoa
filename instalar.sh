#!/usr/bin/env bash
# Instalador del Despacho Pessoa para macOS y Linux.
# Uso: abre la Terminal, escribe «bash » (con un espacio), arrastra este archivo a la ventana y pulsa Enter.
# Opciones para pruebas: --simular (no instala nada), --herramienta claude|opencode|codex|ninguna, --si (sin preguntas)
set -euo pipefail
cd "$(dirname "$0")"
AYUDA="docs/guias/problemas-frecuentes.md"
CLAUDE_MINIMA="2.1.295"  # desde esta versión los controles (hooks) bloquean siempre
SIMULAR=0
SI=0
HERRAMIENTA=""
while [ $# -gt 0 ]; do
  case "$1" in
    --simular) SIMULAR=1 ;;
    --si) SI=1 ;;
    --herramienta) [ $# -ge 2 ] || { echo "Falta el nombre de la herramienta después de --herramienta"; exit 2; }
                   HERRAMIENTA="$2"; shift ;;
    *) echo "Opción desconocida: $1"; exit 2 ;;
  esac
  shift
done

paso() { printf '\n[%s/4] %s\n' "$1" "$2"; }
bien() { printf '  ✔ %s\n' "$1"; }
donde_ayuda() {  # donde_ayuda <ancla>; el ancla llega como '#python'
  printf '  Qué hacer: abre el archivo %s de esta carpeta, sección %s.\n' "$AYUDA" "$1"
}
falla() { printf '  ✘ %s\n' "$1"; donde_ayuda "$2"; exit 1; }
aviso() { printf '  ! %s\n' "$1"; donde_ayuda "$2"; }
tiene() { command -v "$1" >/dev/null 2>&1; }
buscar_python() {
  for c in python3 python; do
    if tiene "$c" && [ "$("$c" -c 'import sys; print(int(sys.version_info >= (3, 10)))' 2>/dev/null)" = "1" ]; then
      echo "$c"; return 0
    fi
  done
  return 0  # sin esto, «set -e» cerraría el script cuando no hay Python
}
version_menor() {  # version_menor A B: cierto si A < B, comparando número a número (macOS no trae «sort -V»)
  local IFS=. a b i
  set -f
  a=($1); b=($2)
  set +f
  for i in 0 1 2; do
    if [ "${a[$i]:-0}" -lt "${b[$i]:-0}" ]; then return 0; fi
    if [ "${a[$i]:-0}" -gt "${b[$i]:-0}" ]; then return 1; fi
  done
  return 1
}
version_claude() {  # imprime la versión instalada (x.y.z) o nada si no se pudo leer
  local salida
  salida="$(claude --version 2>/dev/null || true)"
  printf '%s\n' "$salida" | sed -n 's/.*\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' | head -n 1
}
instalar_brew() {  # instalar_brew <paquete> <nombre> <ancla>
  if [ "$SIMULAR" = 1 ]; then echo "  (simulación) brew install $1"; return; fi
  tiene brew || falla "No encontré Homebrew para instalar $2. Instálalo desde https://brew.sh o instala $2 a mano." "$3"
  echo "  Instalando $2 con Homebrew..."
  brew install "$1" || falla "Homebrew no pudo instalar $2." "$3"
}

echo "Instalador del Despacho Pessoa"
echo "Voy a comprobar Python, instalar la herramienta que elijas y probar que todo funciona."
if [ "$SI" != 1 ]; then
  read -r -p "¿Continuar? (S/n) " r
  case "$r" in ""|[sSyY]*) ;; *) echo "No hice nada. Hasta pronto."; exit 0 ;; esac
fi

paso 1 "Python 3 (lo usan la calculadora de plazos y los validadores)"
PY="$(buscar_python)"
if [ -z "$PY" ]; then instalar_brew python "Python 3" "#python"; PY="$(buscar_python)"; fi
if [ -n "$PY" ]; then bien "Python listo ($PY)."
elif [ "$SIMULAR" = 1 ]; then echo "  (simulación) Python no disponible: en una instalación real aquí se instalaría y se volvería a comprobar."
else falla "Python 3.10 o posterior no quedó disponible." "#python"
fi

paso 2 "La herramienta"
if [ -z "$HERRAMIENTA" ]; then
  if [ "$SI" = 1 ]; then HERRAMIENTA=ninguna; else
    echo "  ¿Con qué herramienta quieres trabajar?"
    echo "    1. Claude Code    2. OpenCode    3. Codex    4. Aún no sé (no instalo ninguna)"
    read -r -p "  Escribe el número: " op
    case "$op" in 1) HERRAMIENTA=claude ;; 2) HERRAMIENTA=opencode ;; 3) HERRAMIENTA=codex ;; *) HERRAMIENTA=ninguna ;; esac
  fi
fi
case "$HERRAMIENTA" in
  claude)   NOMBRE="Claude Code"; NPM="@anthropic-ai/claude-code"; COMANDO=claude;   GUIA=nivel-2-claude-code.md
            PRIMERO="@01-observador-caeiro Lee casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribe casos/mi-primer-caso/02-hechos/hechos.md según tu contrato de salida." ;;
  opencode) NOMBRE="OpenCode";    NPM="opencode-ai";               COMANDO=opencode; GUIA=nivel-2-opencode.md
            PRIMERO="@01-observador-caeiro Lee casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribe casos/mi-primer-caso/02-hechos/hechos.md según tu contrato de salida." ;;
  codex)    NOMBRE="Codex";       NPM="@openai/codex";             COMANDO=codex;    GUIA=nivel-2-codex.md
            PRIMERO="Usa el agente 01-observador-caeiro para leer casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribir casos/mi-primer-caso/02-hechos/hechos.md según su contrato de salida." ;;
  ninguna)  ;;
  *) echo "Herramienta desconocida: $HERRAMIENTA"; exit 2 ;;
esac
if [ "$HERRAMIENTA" = ninguna ]; then
  echo "  No instalo ninguna. Puedes volver a ejecutar el instalador cuando decidas."
else
  if tiene node; then bien "Node listo ($(node --version))."; else
    instalar_brew node "Node" "#node"
    [ "$SIMULAR" = 1 ] || tiene node || falla "Node no quedó disponible." "#node"
  fi
  if tiene "$COMANDO"; then
    bien "$NOMBRE ya está instalado."
    if [ "$HERRAMIENTA" = claude ]; then
      V="$(version_claude)"
      if [ -n "$V" ] && version_menor "$V" "$CLAUDE_MINIMA"; then
        aviso "Tu Claude Code es la versión $V; el despacho necesita $CLAUDE_MINIMA o posterior para que los controles bloqueen siempre. Actualiza con: npm install -g @anthropic-ai/claude-code@latest" "#confianza-carpeta"
      fi
    fi
  elif [ "$SIMULAR" = 1 ]; then echo "  (simulación) npm install -g $NPM"
  else
    echo "  Instalando $NOMBRE (npm install -g $NPM)..."
    npm install -g "$NPM" || falla "npm no pudo instalar $NOMBRE." "#instalar-herramienta"
    bien "$NOMBRE instalado."
  fi
fi

paso 3 "Compruebo que el despacho funciona"
if [ -z "$PY" ]; then
  echo "  (simulación) se omite la comprobación: no hay Python con el que correrla."
else
  "$PY" herramientas/verificar_corpus.py --comprobar || falla "El corpus de fuentes/ no coincide con su sello." "#verificacion"
  "$PY" herramientas/calcular_plazos.py --demo-casos >/dev/null || falla "La calculadora de plazos no corrió." "#verificacion"
  bien "Corpus intacto y calculadora funcionando."
fi

paso 4 "Listo"
if [ "$HERRAMIENTA" = ninguna ]; then
  echo "  Puedes usar el despacho en el chat: abre docs/guias/nivel-1-chat.md."
else
  echo "  1. En la Terminal, entra a esta carpeta: cd \"$(pwd)\""
  echo "  2. Escribe: $COMANDO"
  if [ "$HERRAMIENTA" = opencode ]; then echo "  3. Escribe:"; else echo "  3. Cuando pregunte si confías en la carpeta, responde que sí. Luego escribe:"; fi
  echo "     $PRIMERO"
  echo "  Guía paso a paso: docs/guias/$GUIA"
fi
