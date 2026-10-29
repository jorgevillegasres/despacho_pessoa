"""Ejecuta de verdad el `command:` que el generador escribe para los hooks de Claude Code,
con intérpretes falsos en el PATH (macOS: solo python3; Windows: tiendas falsas y solo py)."""
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "despacho"))
import generar_adaptadores as ga  # noqa: E402

BASH = shutil.which("bash")
BASH_USABLE = bool(BASH) and "system32" not in BASH.lower()
AGENTE = "01-observador-caeiro"


def posix(ruta) -> str:
    s = str(ruta).replace("\\", "/")
    m = re.match(r"^([A-Za-z]):(/.*)$", s)
    return f"/{m.group(1).lower()}{m.group(2)}" if m and os.name == "nt" else s


@unittest.skipUnless(BASH_USABLE, "no hay bash utilizable (en Windows hace falta Git Bash)")
class TestLanzadorHook(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, True)

    def interprete(self, nombre, real):
        cuerpo = f'exec "{posix(sys.executable)}" "$@"\n' if real else "exit 49\n"
        ruta = self.dir / nombre
        ruta.write_text("#!/bin/sh\n" + cuerpo, encoding="utf-8", newline="\n")
        ruta.chmod(ruta.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def lanzar(self, ruta_destino, con_project_dir=True):
        cmd = ga.comando_hook(AGENTE)
        payload = {"tool_name": "Write", "cwd": str(RAIZ),
                   "tool_input": {"file_path": ruta_destino, "content": "x"}}
        env = {"PATH": posix(self.dir), "CLAUDE_PROJECT_DIR": posix(RAIZ) if con_project_dir else "",
               "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""), "DESPACHO_PERMISOS": ""}
        env = {k: v for k, v in env.items() if v}
        return subprocess.run([BASH, "-c", cmd], input=json.dumps(payload), capture_output=True,
                              text=True, encoding="utf-8", env=env, cwd=tempfile.gettempdir())

    def comprobar_hook_real(self):
        r = self.lanzar("casos/caso-prueba/borrador.md")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("BLOQUEADO POR EL DESPACHO PESSOA", r.stderr)
        self.assertIn("Regla 4", r.stderr)  # lo dijo hook_claude.py, no el mensaje del lanzador
        # Si la sonda consumiera stdin, el hook vería JSON vacío y bloquearía: un 0 prueba que llegó.
        r = self.lanzar("casos/caso-prueba/hechos.md")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_solo_python3_real_caso_mac(self):
        self.interprete("python3", True)
        self.comprobar_hook_real()

    def test_python_y_python3_son_tiendas_falsas_y_py_real_caso_windows(self):
        self.interprete("python3", False)
        self.interprete("python", False)
        self.interprete("py", True)
        self.comprobar_hook_real()

    def test_sin_claude_project_dir_y_fuera_de_la_raiz_bloquea(self):
        # El cwd del lanzador es la carpeta temporal, no el repositorio: "./herramientas/hook_claude.py"
        # no existe y el hook debe fallar cerrado (exit 2), aun para una escritura permitida.
        self.interprete("python3", True)
        r = self.lanzar("casos/caso-prueba/hechos.md", con_project_dir=False)
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_ningun_interprete_sirve_bloquea_con_mensaje(self):
        for n in ("python3", "python", "py"):
            self.interprete(n, False)
        r = self.lanzar("casos/caso-prueba/hechos.md")
        self.assertEqual(r.returncode, 2)
        self.assertIn("no encontré Python", r.stderr)


if __name__ == "__main__":
    unittest.main()
