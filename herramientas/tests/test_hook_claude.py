import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
HOOK = RAIZ / "herramientas" / "hook_claude.py"


def correr(agente, payload, env=None):
    return subprocess.run([sys.executable, str(HOOK), agente], input=json.dumps(payload),
                          capture_output=True, text=True, cwd=RAIZ, encoding="utf-8", env=env)


class TestHook(unittest.TestCase):
    def test_write_permitido(self):
        r = correr("01-observador-caeiro", {"tool_name": "Write",
                   "tool_input": {"file_path": "casos/caso-prueba/hechos.md", "content": "x"}})
        self.assertEqual(r.returncode, 0)

    def test_write_denegado_sale_2_y_explica(self):
        r = correr("01-observador-caeiro", {"tool_name": "Write",
                   "tool_input": {"file_path": "casos/caso-prueba/borrador.md", "content": "x"}})
        self.assertEqual(r.returncode, 2)
        self.assertIn("Regla 4", r.stderr)

    def test_edit_usa_file_path(self):
        r = correr("03-redactor-reis", {"tool_name": "Edit",
                   "tool_input": {"file_path": "fuentes/00_transversal/constitucion_art_23_86.md",
                                  "old_string": "a", "new_string": "b"}})
        self.assertEqual(r.returncode, 2)

    def test_read_privado_denegado(self):
        r = correr("02-investigador-search", {"tool_name": "Read",
                   "tool_input": {"file_path": "casos/caso-prueba-2/privado/notas-privado.md"}})
        self.assertEqual(r.returncode, 2)

    def test_bash_calculadora_permitida_a_caeiro(self):
        r = correr("01-observador-caeiro", {"tool_name": "Bash",
                   "tool_input": {"command": "python herramientas/calcular_plazos.py --modo peticion --fecha-inicio 2026-09-25"}})
        self.assertEqual(r.returncode, 0)

    def test_bash_soares_no_cambia_la_raiz_del_corpus(self):
        r = correr("04-verificador-soares", {"tool_name": "Bash", "tool_input": {
            "command": "python herramientas/verificar_citas.py casos/x/borrador.md --raiz herramientas/tests/datos"}})
        self.assertEqual(r.returncode, 2)
        self.assertIn("raíz del corpus", r.stderr)
        r = correr("04-verificador-soares", {"tool_name": "Bash", "tool_input": {
            "command": "python herramientas/verificar_citas.py casos/x/borrador.md"}})
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_bash_otro_comando_denegado(self):
        r = correr("01-observador-caeiro", {"tool_name": "Bash", "tool_input": {"command": "curl https://example.com"}})
        self.assertEqual(r.returncode, 2)

    def test_glob_sin_path_base_permitida(self):
        r = correr("02-investigador-search", {"tool_name": "Glob", "tool_input": {"pattern": "fuentes/**/*.md"}})
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_glob_sin_path_base_vacia_denegado(self):
        r = correr("02-investigador-search", {"tool_name": "Glob", "tool_input": {"pattern": "**/*.md"}})
        self.assertEqual(r.returncode, 2)

    def test_glob_con_punto_punto_denegado(self):
        r = correr("02-investigador-search", {"tool_name": "Glob", "tool_input": {"pattern": "../**"}})
        self.assertEqual(r.returncode, 2)

    def test_glob_llave_como_comodin_denegado(self):
        r = correr("02-investigador-search", {"tool_name": "Glob", "tool_input": {"pattern": "{casos,fuentes}/**"}})
        self.assertEqual(r.returncode, 2)

    def test_glob_punto_punto_incrustado_denegado(self):
        r = correr("02-investigador-search", {"tool_name": "Glob", "tool_input": {"pattern": "fuentes/..hack/*"}})
        self.assertEqual(r.returncode, 2)

    def test_glob_absoluto_denegado(self):
        r = correr("02-investigador-search", {"tool_name": "Glob", "tool_input": {"pattern": "/etc/*"}})
        self.assertEqual(r.returncode, 2)

    def test_grep_sin_path_denegado(self):
        r = correr("02-investigador-search", {"tool_name": "Grep", "tool_input": {"pattern": "x"}})
        self.assertEqual(r.returncode, 2)
        r = correr("02-investigador-search", {"tool_name": "Grep",
                   "tool_input": {"pattern": "x", "output_mode": "content"}})
        self.assertEqual(r.returncode, 2)

    def test_grep_sin_path_con_glob_denegado(self):
        r = correr("02-investigador-search", {"tool_name": "Grep",
                   "tool_input": {"pattern": "x", "glob": "fuentes/**/*.md"}})
        self.assertEqual(r.returncode, 2)  # el cwd (raíz) no es legible

    def test_grep_con_path_fuera_denegado(self):
        r = correr("02-investigador-search", {"tool_name": "Grep",
                   "tool_input": {"pattern": "x", "path": "casos/caso-prueba/privado"}})
        self.assertEqual(r.returncode, 2)

    def test_herramienta_web_denegada(self):
        r = correr("02-investigador-search", {"tool_name": "WebFetch", "tool_input": {"url": "https://x"}})
        self.assertEqual(r.returncode, 2)
        self.assertIn("internet", r.stderr.lower())

    def test_json_invalido_bloquea(self):
        r = subprocess.run([sys.executable, str(HOOK), "01-observador-caeiro"], input="no es json",
                           capture_output=True, text=True, cwd=RAIZ, encoding="utf-8")
        self.assertEqual(r.returncode, 2)
        self.assertIn("ilegible", r.stderr)

    def test_argv_incorrecto_bloquea(self):
        r = subprocess.run([sys.executable, str(HOOK)], input="{}", capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 2)

    def test_tool_name_no_str_bloquea_sin_traceback(self):
        r = correr("01-observador-caeiro", {"tool_name": ["Write"], "tool_input": {}})
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("BLOQUEADO", r.stderr)

    def test_tool_input_no_dict_bloquea(self):
        r = correr("02-investigador-search", {"tool_name": "Grep", "tool_input": "x"})
        self.assertEqual(r.returncode, 2)

    def test_bom_y_ruta_con_acento(self):
        entrada = "\ufeff".encode("utf-8") + json.dumps({"tool_name": "Write",
                   "tool_input": {"file_path": "casos/caso-ñ/hechos.md"}}).encode("utf-8")
        r = subprocess.run([sys.executable, str(HOOK), "01-observador-caeiro"], input=entrada,
                           capture_output=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_herramientas_inocuas(self):
        for h in ["TodoWrite", "AskUserQuestion", "BashOutput", "KillShell", "ExitPlanMode", "EnterPlanMode"]:
            r = correr("01-observador-caeiro", {"tool_name": h, "tool_input": {}})
            self.assertEqual(r.returncode, 0, h)

    def test_herramienta_desconocida_bloquea(self):
        r = correr("01-observador-caeiro", {"tool_name": "Inventada", "tool_input": {}})
        self.assertEqual(r.returncode, 2)
        self.assertIn("no autorizada", r.stderr)

    def test_delegar_bloquea(self):
        for h in ["Agent", "Task"]:
            r = correr("01-observador-caeiro", {"tool_name": h, "tool_input": {}})
            self.assertEqual(r.returncode, 2, h)
            self.assertIn("delegar", r.stderr)

    def test_powershell_usa_regla_ejecuta(self):
        r = correr("01-observador-caeiro", {"tool_name": "PowerShell", "tool_input": {"command": "Remove-Item x"}})
        self.assertEqual(r.returncode, 2)
        r = correr("01-observador-caeiro", {"tool_name": "PowerShell",
                   "tool_input": {"command": "python herramientas/calcular_plazos.py --modo peticion --fecha-inicio 2026-09-25"}})
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_notebookread_usa_notebook_path(self):
        r = correr("02-investigador-search", {"tool_name": "NotebookRead",
                   "tool_input": {"notebook_path": "casos/caso-prueba/privado/n.ipynb"}})
        self.assertEqual(r.returncode, 2)

    def test_cwd_relativo_se_ignora(self):
        r = correr("01-observador-caeiro", {"cwd": "casos", "tool_name": "Write",
                   "tool_input": {"file_path": "caso-prueba/hechos.md"}})
        self.assertEqual(r.returncode, 2)

    def test_permisos_alternos_por_variable_de_entorno(self):
        permisos = {"x-web": {"lee": ["fuentes/**"], "escribe": ["notas.md"], "ejecuta": [], "internet": True}}
        with tempfile.TemporaryDirectory() as d:
            ruta = os.path.join(d, "permisos.json")
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(permisos, f)
            env = dict(os.environ, DESPACHO_PERMISOS=ruta)
            r = correr("x-web", {"tool_name": "WebFetch", "tool_input": {"url": "https://x"}}, env=env)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = correr("x-web", {"tool_name": "mcp__x__y", "tool_input": {}}, env=env)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = correr("x-web", {"tool_name": "Write", "tool_input": {"file_path": "otro.md"}}, env=env)
            self.assertEqual(r.returncode, 2)

    def test_cwd_del_payload_se_respeta(self):
        r = correr("01-observador-caeiro", {"cwd": str(RAIZ / "casos"), "tool_name": "Write",
                   "tool_input": {"file_path": "caso-prueba/hechos.md"}})
        self.assertEqual(r.returncode, 0)

    def test_write_con_punto_punto_que_escapa_denegado(self):
        r = correr("01-observador-caeiro", {"tool_name": "Write",
                   "tool_input": {"file_path": "casos/../../fuera/hechos.md", "content": "x"}})
        self.assertEqual(r.returncode, 2)

    def test_conector_mcp_denegado(self):
        r = correr("02-investigador-search", {"tool_name": "mcp__anything__tool", "tool_input": {}})
        self.assertEqual(r.returncode, 2)
        self.assertIn("conectores", r.stderr.lower())

    def test_write_sin_file_path_falla_cerrado(self):
        r = correr("01-observador-caeiro", {"tool_name": "Write", "tool_input": {"content": "x"}})
        self.assertEqual(r.returncode, 2)
        self.assertIn("ruta", r.stderr.lower())


if __name__ == "__main__":
    unittest.main()
