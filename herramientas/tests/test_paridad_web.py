import json, shutil, subprocess, sys, unittest
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))
import calcular_plazos as cp  # noqa: E402

NODE = shutil.which("node")
PUENTE = RAIZ / "web" / "tests" / "paridad.js"
CLI = RAIZ / "herramientas" / "calcular_plazos.py"

# (modo, inicio, corte o None = fecha de hoy, días personalizados, con detalle)
REPORTES = [
    ("peticion", "2026-09-25", "2026-10-30", None, True),          # petici?n
    ("peticion", "2026-10-08", "2026-10-30", None, True),          # vence hoy
    ("peticion", "2026-10-10", "2026-10-30", None, False),         # radicación en sábado
    ("peticion", "2026-10-12", "2026-10-30", None, False),         # radicación en festivo
    ("peticion", "2026-10-08", None, None, True),                  # corte de hoy
    ("fallo_tutela", "2026-12-15", "2026-12-30", None, True),      # cruza festivos de diciembre
    ("impugnacion", "2026-10-30", "2026-10-30", None, True),
    ("cumplimiento_48h", "2026-10-09", "2026-10-30", None, False), # vencido
    ("cumplimiento_48h", "2026-10-09", "2026-10-11", None, False), # vence hoy
    ("peticion", "2026-10-08", "2026-10-30", 5, True),             # días personalizados
    ("peticion", "2026-11-05", "2026-10-30", None, True),          # error: inicio posterior
    ("peticion", "2026-11-05", "2026-10-30", 0, True),             # error: días antes que fechas
    ("peticion_consulta", "2027-11-25", "2027-12-30", None, True), # error: cruza a 2028
]


def node(casos):
    r = subprocess.run([NODE, str(PUENTE)], input=json.dumps(casos), capture_output=True,
                       text=True, encoding="utf-8", cwd=RAIZ)
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


def cli(modo, inicio, corte, dias, detalle):
    args = [sys.executable, str(CLI), "--modo", modo, "--fecha-inicio", inicio]
    if corte:
        args += ["--fecha-actual", corte]
    if dias is not None:
        args += ["--dias", str(dias)]
    if not detalle:
        args.append("--sin-detalle")
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
    return r.stdout.rstrip("\n")


@unittest.skipUnless(NODE, "Node no está instalado")
class TestParidadWeb(unittest.TestCase):
    def test_vencimientos_cada_dia_de_2026_y_2027(self):
        casos, esperado = [], []
        d = date(2026, 1, 1)
        while d.year < 2028:
            for n in (3, 10, 15, 30):
                casos.append({"tipo": "vencimiento", "inicio": d.isoformat(), "n": n})
                try:
                    r = cp.calcular_vencimiento(d, n)
                    esperado.append({"vencimiento": r["fecha_vencimiento"].isoformat(),
                                     "festivos": r["festivos_cruzados"]})
                except cp.ErrorDeEntrada as e:
                    esperado.append({"error": str(e)})
            d += timedelta(days=1)
        obtenido = node(casos)
        self.assertEqual(len(obtenido), len(esperado))
        for caso, o, e in zip(casos, obtenido, esperado):
            self.assertEqual(o, e, f"Python y JavaScript discrepan en {caso}")

    def test_reporte_completo_identico_al_de_la_terminal(self):
        casos = [{"tipo": "reporte", "modo": m, "inicio": i, "corte": c or cp.fecha_de_hoy().isoformat(),
                  "dias": d, "detalle": det, "cortePorDefecto": c is None}
                 for m, i, c, d, det in REPORTES]
        obtenido = node(casos)
        self.assertEqual(len(obtenido), len(REPORTES))
        for caso, js, args in zip(casos, obtenido, REPORTES):
            with self.subTest(caso=args):
                texto_js = js["texto"] if "texto" in js else f"No puedo calcular: {js['error']}"
                self.assertEqual(texto_js, cli(*args))


if __name__ == "__main__":
    unittest.main()
