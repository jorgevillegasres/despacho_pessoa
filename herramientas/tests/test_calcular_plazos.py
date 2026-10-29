import json, subprocess, sys, tempfile, unittest
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))
import calcular_plazos as cp  # noqa: E402


class TestCalculo(unittest.TestCase):
    def test_radicacion_jueves_con_festivo_intermedio_vence_15_habil(self):
        r = cp.calcular_vencimiento(date(2026, 10, 8), 15)
        self.assertEqual(r["fecha_vencimiento"], date(2026, 10, 30))
        self.assertIn("2026-10-12", " ".join(r["festivos_cruzados"]))
        t = cp.contar_dias_habiles_transcurridos(date(2026, 10, 8), date(2026, 10, 30))
        self.assertEqual(t["habiles_transcurridos"], 15)

    def test_caso_01_peticion_25_sep_vence_19_oct(self):
        r = cp.calcular_vencimiento(date(2026, 9, 25), 15)
        self.assertEqual(r["fecha_vencimiento"], date(2026, 10, 19))

    def test_festivos_2027_cargados(self):
        self.assertIn(date(2027, 3, 25), cp.FESTIVOS)
        self.assertEqual(cp.AÑOS_CARGADOS, {2026, 2027})

    def test_inicio_posterior_a_corte_es_error(self):
        with self.assertRaises(cp.ErrorDeEntrada):
            cp.validar_fechas(date(2026, 11, 1), date(2026, 10, 30))

    def test_año_sin_festivos_es_error(self):
        with self.assertRaises(cp.ErrorDeEntrada):
            cp.validar_fechas(date(2030, 1, 1), date(2030, 2, 1))

    def test_vencimiento_fuera_de_años_cargados_es_error(self):
        with self.assertRaises(cp.ErrorDeEntrada):
            cp.calcular_vencimiento(date(2027, 12, 20), 30)

    def test_modo_48h_cuenta_horas_no_dias_habiles(self):
        r = cp.calcular_vencimiento_horas(date(2026, 10, 9), 48)   # viernes
        self.assertEqual(r["fecha_vencimiento"], date(2026, 10, 11))  # domingo: 48 h son 48 h

    def test_dias_menor_a_uno_es_error(self):
        with self.assertRaises(cp.ErrorDeEntrada):
            cp.calcular_vencimiento(date(2026, 10, 8), 0)

    def test_2027_completo(self):
        esperadas = {date.fromisoformat(x) for x in (
            "2027-01-01", "2027-01-11", "2027-03-22", "2027-03-25", "2027-03-26", "2027-05-01",
            "2027-05-10", "2027-05-31", "2027-06-07", "2027-07-05", "2027-07-20", "2027-08-07",
            "2027-08-16", "2027-10-18", "2027-11-01", "2027-11-15", "2027-12-08", "2027-12-25")}
        self.assertEqual({d for d in cp.FESTIVOS if d.year == 2027}, esperadas)
        self.assertEqual(len(esperadas), 18)

    def test_36_horas_es_error(self):
        with self.assertRaises(cp.ErrorDeEntrada):
            cp.calcular_vencimiento_horas(date(2026, 10, 9), 36)

    def test_horas_vencimiento_fuera_de_años_es_error(self):
        with self.assertRaises(cp.ErrorDeEntrada):
            cp.calcular_vencimiento_horas(date(2027, 12, 31), 48)

    def test_cargar_festivos_archivo_invalido(self):
        with tempfile.TemporaryDirectory() as d:
            malo = Path(d) / "x.json"
            malo.write_text("{no es json", encoding="utf-8")
            with self.assertRaises(cp.ErrorDeEntrada):
                cp.cargar_festivos(malo)
            incoherente = Path(d) / "y.json"
            incoherente.write_text(json.dumps({"2026": {"2027-01-01": "x"}}), encoding="utf-8")
            with self.assertRaises(cp.ErrorDeEntrada):
                cp.cargar_festivos(incoherente)
            with self.assertRaises(cp.ErrorDeEntrada):
                cp.cargar_festivos(Path(d) / "no_existe.json")

    def test_festivos_coinciden_con_la_ley_51_de_1983(self):
        def pascua(a):  # algoritmo gregoriano anónimo
            g, c = a % 19, a // 100
            h = (c - c // 4 - (8 * c + 13) // 25 + 19 * g + 15) % 30
            i = h - (h // 28) * (1 - (h // 28) * (29 // (h + 1)) * ((21 - g) // 11))
            j = (a + a // 4 + i + 2 - c + c // 4) % 7
            mes = 3 + (i - j + 40) // 44
            return date(a, mes, i - j + 28 - 31 * (mes // 4))

        def al_lunes(d):
            return d if d.weekday() == 0 else d + timedelta(days=(7 - d.weekday()) % 7)

        self.assertEqual(pascua(2026), date(2026, 4, 5))
        self.assertEqual(pascua(2027), date(2027, 3, 28))
        for a in sorted(cp.AÑOS_CARGADOS):
            p = pascua(a)
            esperados = {date(a, m, d) for m, d in ((1, 1), (5, 1), (7, 20), (8, 7), (12, 8), (12, 25))}
            esperados |= {al_lunes(date(a, m, d)) for m, d in ((1, 6), (3, 19), (6, 29), (8, 15), (10, 12), (11, 1), (11, 11))}
            esperados |= {p - timedelta(days=3), p - timedelta(days=2)}
            esperados |= {al_lunes(p + timedelta(days=n)) for n in (43, 64, 71)}
            self.assertEqual({d for d in cp.FESTIVOS if d.year == a}, esperados, a)

    def test_salida_marca_las_referencias_de_la_herramienta(self):
        r = subprocess.run([sys.executable, str(RAIZ / "herramientas/calcular_plazos.py"),
                            "--fecha-inicio", "2026-10-08", "--fecha-actual", "2026-10-30"],
                           capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
        for linea in r.stdout.splitlines():
            if "Ley 4ª de 1913" in linea or "CGP art. 109" in linea:
                self.assertTrue(linea.endswith("[referencia de la herramienta: no es cita del corpus]"), linea)
        self.assertEqual(r.stdout.count("[referencia de la herramienta: no es cita del corpus]"), 2)

    def test_json_no_incluye_ley_2578(self):
        datos = json.loads(cp.RUTA_FESTIVOS.read_text(encoding="utf-8"))
        self.assertIn("_pendiente_decision_abogado", datos)
        self.assertNotIn(date(2026, 7, 13), cp.FESTIVOS)
        self.assertNotIn(date(2027, 7, 12), cp.FESTIVOS)


class TestCLI(unittest.TestCase):
    def correr(self, *args):
        return subprocess.run([sys.executable, str(RAIZ / "herramientas/calcular_plazos.py"), *args],
                              capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)

    def test_cli_peticion_con_festivo_intermedio(self):
        r = self.correr("--modo", "peticion", "--fecha-inicio", "2026-10-08", "--fecha-actual", "2026-10-30")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2026-10-30", r.stdout)
        self.assertIn("15 días hábiles", r.stdout)

    def test_cli_rechaza_inicio_posterior(self):
        r = self.correr("--modo", "peticion", "--fecha-inicio", "2026-11-05", "--fecha-actual", "2026-10-30")
        self.assertEqual(r.returncode, 2)
        self.assertIn("posterior", r.stdout + r.stderr)

    def test_cli_dias_cero_o_negativo(self):
        for d in ("0", "-3"):
            r = self.correr("--fecha-inicio", "2026-10-08", "--dias", d)
            self.assertEqual(r.returncode, 2)
            self.assertIn("al menos 1", r.stdout + r.stderr)

    def test_cli_modo_48h(self):
        r = self.correr("--modo", "cumplimiento_48h", "--fecha-inicio", "2026-10-09", "--fecha-actual", "2026-10-30")
        self.assertEqual(r.returncode, 0)
        self.assertIn("48 horas", r.stdout)
        self.assertIn("2026-10-11", r.stdout)

    def test_cli_cruce_de_año(self):
        r = self.correr("--fecha-inicio", "2026-12-20", "--fecha-actual", "2026-12-30")
        self.assertEqual(r.returncode, 0)
        self.assertIn("2027-01-01", r.stdout)
        self.assertIn("2027-01-11", r.stdout)

    def test_cli_fecha_actual_por_defecto_etiquetada(self):
        r = self.correr("--fecha-inicio", "2026-10-08")
        self.assertEqual(r.returncode, 0)
        self.assertIn("fecha de referencia por defecto", r.stdout)

    def test_cli_radicacion_sabado_avisa(self):
        r = self.correr("--fecha-inicio", "2026-10-10")
        self.assertEqual(r.returncode, 0)
        self.assertIn("AVISO", r.stdout)
        self.assertIn("inhábil", r.stdout)

    def test_cli_radicacion_festivo_avisa(self):
        r = self.correr("--fecha-inicio", "2026-10-12")
        self.assertIn("AVISO", r.stdout)
        self.assertIn("Festivo", r.stdout)

    def test_cli_radicacion_habil_sin_aviso(self):
        r = self.correr("--fecha-inicio", "2026-10-08")
        self.assertNotIn("AVISO", r.stdout)

    def test_cli_vence_hoy_y_nota_hora(self):
        r = self.correr("--fecha-inicio", "2026-10-08", "--fecha-actual", "2026-10-30", "--sin-detalle")
        self.assertIn("EN CURSO — vence hoy", r.stdout)
        self.assertIn("vence en esta fecha", r.stdout)
        self.assertIn("CGP art. 109", r.stdout)
        self.assertIn("Regla de cómputo", r.stdout)

    def test_cli_48h_vence_hoy(self):
        r = self.correr("--modo", "cumplimiento_48h", "--fecha-inicio", "2026-10-09", "--fecha-actual", "2026-10-11")
        self.assertIn("vence hoy, a la hora de la notificación", r.stdout)
        self.assertIn("granularidad de día", r.stdout)

    def test_cli_año_sin_festivos_exit_2(self):
        r = self.correr("--fecha-inicio", "2030-01-01", "--fecha-actual", "2030-02-01")
        self.assertEqual(r.returncode, 2)

    def test_cli_cruce_a_año_no_cargado_exit_2(self):
        r = self.correr("--fecha-inicio", "2027-12-20", "--fecha-actual", "2027-12-30", "--dias", "30")
        self.assertEqual(r.returncode, 2)
        self.assertIn("2028", r.stdout)

    def test_demo_sin_frases_juridicas(self):
        r = self.correr("--demo-casos")
        self.assertEqual(r.returncode, 0)
        for frase in ("plenamente cumplida", "silencio administrativo", "operó", "23:59"):
            self.assertNotIn(frase, r.stdout.lower())


if __name__ == "__main__":
    unittest.main()
