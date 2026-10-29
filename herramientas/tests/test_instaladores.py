import os, re, shutil, subprocess, sys, unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AYUDA = RAIZ / "docs" / "guias" / "problemas-frecuentes.md"
POWERSHELL = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
# PATH sin ningún Python: System32 y PowerShell, pero no C:\Windows (ahí vive el lanzador py.exe).
RUTA_WINDOWS_SIN_PYTHON = r"C:\Windows\System32;C:\Windows\System32\WindowsPowerShell\v1.0"
RUTA_UNIX_SIN_PYTHON = "/usr/bin:/bin"


def bash_util():
    """Bash de Git o de macOS/Linux; el bash.exe de System32 es WSL y no sirve aquí."""
    b = shutil.which("bash")
    if b and "system32" not in b.lower():
        return b
    # En CI (windows-latest) el bash de Git no siempre está en el PATH: lo buscamos en su carpeta habitual.
    for base in filter(None, (os.environ.get("ProgramFiles"), os.environ.get("ProgramW6432"))):
        for sub in (r"Git\bin\bash.exe", r"Git\usr\bin\bash.exe"):
            candidato = Path(base) / sub
            if candidato.is_file():
                return str(candidato)
    return None


def correr(args, env=None):
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=RAIZ, timeout=120, env=env)


def primer_comando(archivo, patron):
    """Primera orden de un caso según CLAUDE.md o AGENTS.md, sin las comillas de código."""
    m = re.search(patron, (RAIZ / archivo).read_text(encoding="utf-8"), re.M)
    assert m, f"{archivo}: no encontré el primer comando"
    return m.group(1).replace("`", "").strip()


class TestArchivosDeInstalacion(unittest.TestCase):
    def test_ps1_en_utf8_con_bom(self):
        self.assertTrue((RAIZ / "instalar.ps1").read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_ps1_tolera_el_modo_restringido_al_fijar_la_codificacion(self):
        texto = (RAIZ / "instalar.ps1").read_text(encoding="utf-8-sig")
        self.assertRegex(texto, r"try \{ \[Console\]::OutputEncoding = [^\n]*\} catch \{")

    def test_cmd_lanza_el_ps1_sin_cambiar_la_politica_del_equipo(self):
        texto = (RAIZ / "instalar.cmd").read_text(encoding="ascii")
        self.assertIn("-ExecutionPolicy Bypass", texto)
        self.assertIn('"%~dp0instalar.ps1"', texto)
        self.assertNotIn("Set-ExecutionPolicy", texto)

    def test_cmd_avisa_si_el_zip_no_esta_descomprimido(self):
        texto = (RAIZ / "instalar.cmd").read_text(encoding="ascii")
        self.assertIn('if not exist "%~dp0instalar.ps1"', texto)
        self.assertIn("Primero descomprime el ZIP", texto)

    def test_cmd_con_fin_de_linea_windows(self):
        self.assertIn(b"\r\n", (RAIZ / "instalar.cmd").read_bytes())

    def test_sh_con_fin_de_linea_unix(self):
        self.assertNotIn(b"\r", (RAIZ / "instalar.sh").read_bytes())

    def test_cada_ancla_citada_existe_en_problemas_frecuentes(self):
        definidas = set(re.findall(r'<a id="([a-z0-9-]+)"></a>', AYUDA.read_text(encoding="utf-8")))
        for nombre in ("instalar.ps1", "instalar.sh"):
            citadas = set(re.findall(r"""['"]#([a-z0-9-]+)['"]""", (RAIZ / nombre).read_text(encoding="utf-8-sig")))
            self.assertTrue(citadas, f"{nombre} no cita ninguna ancla")
            self.assertLessEqual(citadas, definidas, f"{nombre}: anclas sin sección: {citadas - definidas}")

    def test_primer_comando_coincide_con_claude_md_y_agents_md(self):
        claude = primer_comando("CLAUDE.md", r"^1\. `(.+)`\s*$")
        codex = primer_comando("AGENTS.md", r"^1\. (.+)$")
        ps1 = dict(re.findall(r"(claude|opencode|codex)\s*=\s*@\{.*?Primero = '([^']+)'",
                              (RAIZ / "instalar.ps1").read_text(encoding="utf-8-sig"), re.S))
        sh = dict(re.findall(r"(claude|opencode|codex)\)\s+NOMBRE=.*?PRIMERO=\"([^\"]+)\"",
                             (RAIZ / "instalar.sh").read_text(encoding="utf-8"), re.S))
        for nombre, primeros in (("instalar.ps1", ps1), ("instalar.sh", sh)):
            self.assertEqual(set(primeros), {"claude", "opencode", "codex"}, nombre)
            self.assertEqual(primeros["claude"], claude, f"{nombre}: Claude Code no coincide con CLAUDE.md")
            self.assertEqual(primeros["opencode"], claude, f"{nombre}: OpenCode no coincide con CLAUDE.md")
            self.assertEqual(primeros["codex"], codex, f"{nombre}: Codex no coincide con AGENTS.md")


@unittest.skipUnless(sys.platform == "win32", "el instalador de PowerShell se prueba en Windows")
class TestInstaladorWindows(unittest.TestCase):
    def ps1(self, *extra, env=None):
        return correr([POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                       str(RAIZ / "instalar.ps1"), "-Simular", "-SinPreguntas", *extra], env=env)

    def test_simulado_sin_herramienta_termina_bien(self):
        r = self.ps1("-Herramienta", "ninguna")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for n in range(1, 5):
            self.assertIn(f"[{n}/4]", r.stdout)
        self.assertIn("Corpus intacto", r.stdout)

    def test_simulado_con_herramienta_no_instala_nada(self):
        for herramienta, npm in (("opencode", "opencode-ai"), ("claude", "@anthropic-ai/claude-code"), ("codex", "@openai/codex")):
            with self.subTest(herramienta=herramienta):
                r = self.ps1("-Herramienta", herramienta)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertTrue(f"(simulación) npm install -g {npm}" in r.stdout or "ya está instalado" in r.stdout, r.stdout)
                self.assertIn("[4/4]", r.stdout)

    def test_simulado_sin_python_no_falla(self):
        env = dict(os.environ)
        env["PATH"] = RUTA_WINDOWS_SIN_PYTHON  # os.environ en Windows guarda las claves en mayúsculas
        r = self.ps1("-Herramienta", "ninguna", env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("(simulación) Python no disponible", r.stdout)
        self.assertIn("(simulación) se omite la comprobación", r.stdout)
        self.assertNotIn("Python listo", r.stdout)
        self.assertEqual(r.stderr.strip(), "", r.stderr)


@unittest.skipUnless(bash_util(), "no hay bash")
class TestInstaladorUnix(unittest.TestCase):
    def sh(self, *args):
        return correr([bash_util(), "instalar.sh", *args])

    def test_simulado_sin_herramienta_termina_bien(self):
        r = self.sh("--simular", "--si", "--herramienta", "ninguna")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for n in range(1, 5):
            self.assertIn(f"[{n}/4]", r.stdout)
        self.assertIn("Corpus intacto", r.stdout)

    def test_opcion_desconocida_sale_con_2(self):
        r = self.sh("--no-existe")
        self.assertEqual(r.returncode, 2)

    def test_herramienta_sin_valor_avisa_y_sale_con_2(self):
        r = self.sh("--herramienta")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Falta el nombre de la herramienta", r.stdout)

    def test_herramienta_desconocida_sale_con_2(self):
        r = self.sh("--simular", "--si", "--herramienta", "foo")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("Herramienta desconocida: foo", r.stdout)

    def test_simulado_sin_python_no_falla(self):
        sonda = correr([bash_util(), "-c", f"PATH={RUTA_UNIX_SIN_PYTHON}; command -v python3 || command -v python"])
        if sonda.returncode == 0:
            self.skipTest(f"hay un Python en {RUTA_UNIX_SIN_PYTHON} ({sonda.stdout.strip()}); no se puede simular su ausencia")
        r = correr([bash_util(), "-c",
                    f"env PATH={RUTA_UNIX_SIN_PYTHON} bash instalar.sh --simular --si --herramienta ninguna"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("(simulación) Python no disponible", r.stdout)
        self.assertIn("(simulación) se omite la comprobación", r.stdout)
        self.assertNotIn("Python listo", r.stdout)


if __name__ == "__main__":
    unittest.main()
