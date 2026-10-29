import json, re, shutil, subprocess, sys, tempfile, tomllib, unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
GEN = RAIZ / "despacho" / "generar_adaptadores.py"
IDS = ["01-observador-caeiro", "02-investigador-search", "03-redactor-reis",
       "04-verificador-soares", "05-diablo-campos"]


def gen(*args):
    return subprocess.run([sys.executable, str(GEN), *args], capture_output=True, text=True,
                          cwd=RAIZ, encoding="utf-8")


class TestGenerador(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = Path(tempfile.mkdtemp())
        r = gen("--salida", str(cls.out))
        assert r.returncode == 0, r.stderr

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def leer(self, rel):
        return (self.out / rel).read_text(encoding="utf-8")

    def test_genera_los_veinte_archivos(self):
        for i in IDS:
            for rel in [f".claude/agents/{i}.md", f".opencode/agents/{i}.md",
                        f".codex/agents/{i}.toml", f"prompts-chat/{i}-chat.md"]:
                self.assertTrue((self.out / rel).exists(), rel)
        self.assertTrue((self.out / "CLAUDE.md").exists())
        self.assertTrue((self.out / "AGENTS.md").exists())

    def test_claude_tiene_hook_y_tools(self):
        t = self.leer(".claude/agents/01-observador-caeiro.md")
        self.assertIn("name: 01-observador-caeiro", t)
        self.assertIn('matcher: "*"', t)
        self.assertIn('onFailure: "block"', t)
        self.assertIn("disallowedTools: WebFetch, WebSearch, Agent, Task", t)
        self.assertIn("tools: Read, Glob, Grep, Write, Edit, Bash\n", t)
        t3 = self.leer(".claude/agents/03-redactor-reis.md")
        self.assertIn("tools: Read, Glob, Grep, Write, Edit\n", t3)
        self.assertNotIn("DESPACHO_PERMISOS", t)

    def test_claude_hook_usa_lanzador_con_varios_interpretes(self):
        t = self.leer(".claude/agents/01-observador-caeiro.md")
        m = re.search(r"^          command: (.*)$", t, re.M)
        self.assertIsNotNone(m)
        cmd = json.loads(m.group(1))
        for pieza in ("python3", "python", "py", "exec",
                      '"${CLAUDE_PROJECT_DIR:-.}/herramientas/hook_claude.py" 01-observador-caeiro',
                      "</dev/null"):
            self.assertIn(pieza, cmd)
        self.assertTrue(cmd.endswith("exit 2"))
        self.assertIn('onFailure: "block"', t)

    def test_opencode_deniega_por_defecto_y_permite_su_archivo(self):
        t = self.leer(".opencode/agents/01-observador-caeiro.md")
        self.assertIn('"*": deny', t)
        self.assertIn('"casos/*/hechos.md": allow', t)
        for i in ("python", "python3", "py"):
            self.assertIn(f'"{i} herramientas/calcular_plazos.py": allow', t)
            self.assertIn(f'"{i} herramientas/calcular_plazos.py *": allow', t)
        self.assertNotIn('"python herramientas/verificar_citas.py": allow', t)
        self.assertIn("webfetch: deny", t)
        self.assertIn("websearch: deny", t)
        self.assertIn("task: deny", t)
        self.assertIn("external_directory: deny", t)
        t3 = self.leer(".opencode/agents/03-redactor-reis.md")
        self.assertIn("bash: deny", t3)

    def test_opencode_lecturas_y_privado_al_final(self):
        t = self.leer(".opencode/agents/02-investigador-search.md")
        bloque = t[t.index("  read:\n"):]
        bloque = bloque[:bloque.index("  edit:")]
        self.assertIn('"*": deny', bloque)
        self.assertIn('"fuentes/**": allow', bloque)
        self.assertIn('"fuentes/*": allow', bloque)
        self.assertIn('"casos/*/hechos.md": allow', bloque)
        lineas = [l for l in bloque.splitlines() if l.strip()]
        self.assertEqual(lineas[-1].strip(), '"casos/*/privado/**": deny')

    def test_opencode_lectura_incluye_el_propio_archivo_de_salida(self):
        t = self.leer(".opencode/agents/01-observador-caeiro.md")
        bloque = t[t.index("  read:\n"):]
        bloque = bloque[:bloque.index("  grep:")]
        self.assertIn('"casos/*/hechos.md": allow', bloque)
        self.assertIn('"casos/*/entrevista-y-pruebas.md": allow', bloque)
        lineas = [l for l in bloque.splitlines() if l.strip()]
        self.assertEqual(lineas[-1].strip(), '"casos/*/privado/**": deny')

    def test_opencode_grep_glob_list_con_los_mismos_patrones_que_read(self):
        t = self.leer(".opencode/agents/02-investigador-search.md")
        def bloque(clave, siguiente):
            b = t[t.index(f"  {clave}:\n"):]
            return b[len(clave) + 4:b.index(f"  {siguiente}:")]
        leer = bloque("read", "grep")
        self.assertIn('"*": deny', leer)
        self.assertEqual(bloque("grep", "glob"), leer)
        self.assertEqual(bloque("glob", "list"), leer)
        self.assertEqual(bloque("list", "edit"), leer)

    def test_prompt_dice_que_puede_leer_su_archivo_de_salida(self):
        for rel in (".claude/agents/01-observador-caeiro.md", "prompts-chat/01-observador-caeiro-chat.md"):
            self.assertIn("Puedes leer tu propio archivo de salida para corregirlo.", self.leer(rel))

    def test_codex_no_finge_sandbox_ni_mcp(self):
        for i in IDS:
            t = self.leer(f".codex/agents/{i}.toml")
            self.assertNotIn("sandbox_mode", t)
            self.assertNotIn("mcp_servers", t)
        for i in ("04-verificador-soares", "05-diablo-campos"):
            self.assertIn("No escribas ningún archivo", self.leer(f".codex/agents/{i}.toml"))
        self.assertNotIn("No escribas ningún archivo", self.leer(".codex/agents/01-observador-caeiro.toml"))

    def test_codex_shell_off_si_no_ejecuta(self):
        for i in ("02-investigador-search", "03-redactor-reis", "05-diablo-campos"):
            datos = tomllib.loads(self.leer(f".codex/agents/{i}.toml"))
            self.assertEqual(datos["features"], {"shell_tool": False})
        for i in ("01-observador-caeiro", "04-verificador-soares"):
            self.assertNotIn("features", tomllib.loads(self.leer(f".codex/agents/{i}.toml")))

    def test_toml_es_valido(self):
        for i in IDS:
            datos = tomllib.loads(self.leer(f".codex/agents/{i}.toml"))
            self.assertEqual(datos["name"], i)
            self.assertIn("## Contrato de salida", datos["developer_instructions"])

    def test_settings_json_de_claude(self):
        texto = self.leer(".claude/settings.json")
        datos = json.loads(texto)
        self.assertIn("Read(./casos/**/privado/**)", datos["permissions"]["deny"])
        self.assertIn("Edit(./fuentes/**)", datos["permissions"]["deny"])
        self.assertNotIn("env", datos)
        self.assertNotIn("DESPACHO_PERMISOS", texto)

    def test_prompt_incluye_permisos_desde_json(self):
        permisos = json.loads((RAIZ / "despacho" / "permisos.json").read_text(encoding="utf-8"))
        t = self.leer("prompts-chat/02-investigador-search-chat.md")
        for ruta in permisos["02-investigador-search"]["lee"]:
            self.assertIn(ruta, t)
        self.assertIn("Reporte de Cierre", t)
        self.assertIn("## Contrato de salida", t)
        self.assertIn("## Permisos y límites", t)
        self.assertIn("Claude Code (hooks) y OpenCode (permisos por ruta)", t)

    def test_chat_incluye_estatuto_y_rutas_para_alumnos(self):
        t = self.leer("prompts-chat/03-redactor-reis-chat.md").split("\n---\n\n", 1)[0]
        self.assertIn("`ESTATUTO.md`", t)
        self.assertIn("`02-hechos/hechos.md` de la carpeta de tu caso", t)
        self.assertNotIn("casos/*/hechos.md", t)
        t2 = self.leer("prompts-chat/02-investigador-search-chat.md").split("\n---\n\n", 1)[0]
        self.assertIn("`fuentes/00_transversal/`", t2)

    def test_permisos_van_antes_de_procedimiento(self):
        t = self.leer(".claude/agents/05-diablo-campos.md")
        self.assertLess(t.index("## Permisos y límites"), t.index("## Procedimiento"))

    def test_archivos_generados_llevan_advertencia(self):
        for rel in [".claude/agents/01-observador-caeiro.md", ".opencode/agents/01-observador-caeiro.md",
                    ".codex/agents/01-observador-caeiro.toml", "prompts-chat/01-observador-caeiro-chat.md",
                    "CLAUDE.md", "AGENTS.md"]:
            self.assertIn("GENERADO", self.leer(rel), rel)

    def test_claude_md_y_agents_md_listan_los_cinco(self):
        c, a = self.leer("CLAUDE.md"), self.leer("AGENTS.md")
        for i in IDS:
            self.assertIn(f"`{i}`", c)
            self.assertIn(f"`{i}`", a)
        self.assertIn("@01-observador-caeiro", c)
        self.assertNotIn("@01-observador-caeiro", a)
        self.assertIn("Usa el agente `01-observador-caeiro`", a)
        self.assertIn("diálogo de confianza", c)
        self.assertNotIn("diálogo de confianza", a)

    def test_claude_md_separa_las_notas_para_el_humano(self):
        c = self.leer("CLAUDE.md")
        self.assertIn("## Nota para quien instala (humano)", c)
        self.assertNotIn("## Nota para quien instala", self.leer("AGENTS.md"))
        reglas = c[c.index("## Reglas para el agente principal"):c.index("## Los agentes y el orden del flujo")]
        for frase in ("diálogo de confianza", "v2.1.295", "settings.local.json"):
            self.assertNotIn(frase, reglas)
        self.assertGreater(c.index("## Nota para quien instala"), c.index("## Validadores"))

    def test_prompt_explica_el_asterisco_y_el_privado(self):
        for rel in (".claude/agents/01-observador-caeiro.md", "prompts-chat/01-observador-caeiro-chat.md"):
            t = self.leer(rel)
            self.assertIn("(El `*` en una ruta significa «cualquier carpeta de caso».)", t)
            self.assertIn("está fuera de tu alcance: no la leas ni la menciones", t)
            self.assertNotIn("no existe para ti", t)
        self.assertIn("Si el comando `python` no funciona en tu equipo", self.leer(".claude/agents/01-observador-caeiro.md"))
        self.assertIn("Bloc de notas (Windows) o TextEdit (Mac)", self.leer("prompts-chat/01-observador-caeiro-chat.md"))

    def test_es_idempotente(self):
        antes = self.leer(".claude/agents/05-diablo-campos.md")
        with tempfile.TemporaryDirectory() as otra:
            self.assertEqual(gen("--salida", otra).returncode, 0)
            self.assertEqual(antes, (Path(otra) / ".claude/agents/05-diablo-campos.md").read_text(encoding="utf-8"))

    def test_claude_md_avisa_de_settings_local(self):
        self.assertIn("settings.local.json", self.leer("CLAUDE.md"))
        self.assertNotIn("settings.local.json", self.leer("AGENTS.md"))

    def test_adaptadores_del_repo_estan_al_dia(self):
        r = gen()
        self.assertEqual(r.returncode, 0, r.stderr)
        st = subprocess.run(["git", "status", "--porcelain", "--", ".claude", ".opencode", ".codex",
                             "prompts-chat", "CLAUDE.md", "AGENTS.md"],
                            capture_output=True, text=True, cwd=RAIZ, encoding="utf-8")
        self.assertEqual(st.stdout.strip(), "", "los adaptadores del repo no coinciden con el núcleo")


class TestNucleoTemporal(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def nucleo(self, editar=None):
        ag = self.tmp / "agentes"
        ag.mkdir(exist_ok=True)
        txt = (RAIZ / "despacho" / "agentes" / "01-observador-caeiro.md").read_text(encoding="utf-8")
        if editar:
            txt = editar(txt)
        (ag / "01-observador-caeiro.md").write_text(txt, encoding="utf-8")
        return ag

    def cambiar(self, clave, valor):
        return lambda t: re.sub(rf"^{clave}:.*$", f"{clave}: {valor}".rstrip(), t, count=1, flags=re.M)

    def test_falla_si_el_nucleo_esta_mal(self):
        ag = self.tmp / "agentes"
        ag.mkdir()
        (ag / "09-roto.md").write_text("---\nid: 09-roto\n---\n## Identidad y oficio\nx\n", encoding="utf-8")
        r = gen("--agentes", str(ag), "--solo-validar")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("09-roto", r.stdout + r.stderr)

    def test_yaml_entrecomilla_descripcion_peligrosa(self):
        ag = self.nucleo(self.cambiar("descripcion", "Hace esto: y # aquello"))
        r = gen("--agentes", str(ag), "--salida", str(self.tmp / "out"))
        self.assertEqual(r.returncode, 0, r.stderr)
        for rel in (".claude/agents/01-observador-caeiro.md", ".opencode/agents/01-observador-caeiro.md"):
            c = (self.tmp / "out" / rel).read_text(encoding="utf-8")
            self.assertIn('description: "Hace esto: y # aquello"', c)
        d = tomllib.loads((self.tmp / "out" / ".codex" / "agents" / "01-observador-caeiro.toml").read_text(encoding="utf-8"))
        self.assertEqual(d["description"], "Hace esto: y # aquello")

    def test_se_niega_a_escribir_sin_salida_con_agentes_ajenos(self):
        ag = self.nucleo()
        r = gen("--agentes", str(ag))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--salida", r.stdout + r.stderr)

    def test_id_distinto_del_nombre_de_archivo(self):
        ag = self.nucleo(lambda t: t.replace("id: 01-observador-caeiro", "id: 02-otro", 1))
        r = gen("--agentes", str(ag), "--solo-validar")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("01-observador-caeiro", r.stdout + r.stderr)

    def test_valor_vacio(self):
        r = gen("--agentes", str(self.nucleo(self.cambiar("cita", ""))), "--solo-validar")
        self.assertNotEqual(r.returncode, 0)

    def test_temperatura_invalida(self):
        r = gen("--agentes", str(self.nucleo(self.cambiar("temperatura", "alta"))), "--solo-validar")
        self.assertNotEqual(r.returncode, 0)

    def test_clave_duplicada(self):
        ag = self.nucleo(lambda t: t.replace("temperatura: 0.1", "temperatura: 0.1\ntemperatura: 0.9", 1))
        r = gen("--agentes", str(ag), "--solo-validar")
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
