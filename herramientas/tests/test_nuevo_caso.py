import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))

import nuevo_caso as nc  # noqa: E402


class TestNuevoCaso(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "casos").mkdir(parents=True)
        (self.tmp / "materias").mkdir(parents=True)
        shutil.copytree(RAIZ / "casos" / "_PLANTILLA-CASO", self.tmp / "casos" / "_PLANTILLA-CASO")
        shutil.copytree(RAIZ / "materias" / "tutela", self.tmp / "materias" / "tutela")
        (self.tmp / "casos" / "00-indice.md").write_text(
            "# Índice\n\n| ID | Caso | Materia | Área | Cliente | Estado | Próximo plazo | Responsable | Última actualización |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "<!-- CASOS-NUEVOS -->\n",
            encoding="utf-8",
        )

    def crear(self, nombre="Caso de prueba", **kwargs):
        return nc.crear_caso(
            raiz=self.tmp,
            nombre=nombre,
            materia=kwargs.pop("materia", "tutela"),
            fecha=kwargs.pop("fecha", "2026-10-28"),
            **kwargs,
        )

    def test_crea_caso_y_reemplaza_marcadores(self):
        r = self.crear(area="laboral", cliente="Cliente ficticio")
        self.assertEqual(r["id"], "CASO-2026-001")
        self.assertEqual(r["slug"], "caso-de-prueba")
        expediente = (self.tmp / "casos" / "caso-de-prueba" / "00-expediente.md").read_text(encoding="utf-8")
        for texto in ("CASO-2026-001", "Caso de prueba", "tutela", "laboral",
                      "plantillas/modelo-tutela.md", "fuentes/00_transversal",
                      "Socio Director", "usted", "formal", "completa"):
            self.assertIn(texto, expediente)
        self.assertNotIn("{{", expediente)
        entrada = (self.tmp / "casos" / "caso-de-prueba" / "01-entrada" / "entrevista-y-pruebas.md").read_text(encoding="utf-8")
        self.assertIn("Caso de prueba", entrada)
        self.assertNotIn("{{NOMBRE}}", entrada)

    def test_agrega_fila_al_indice(self):
        self.crear()
        indice = (self.tmp / "casos" / "00-indice.md").read_text(encoding="utf-8")
        self.assertIn("CASO-2026-001", indice)
        self.assertIn("caso-de-prueba", indice)
        self.assertIn("<!-- CASOS-NUEVOS -->", indice)

    def test_siguiente_id(self):
        uno = self.crear("Primer caso")
        dos = self.crear("Segundo caso")
        self.assertEqual(uno["id"], "CASO-2026-001")
        self.assertEqual(dos["id"], "CASO-2026-002")

    def test_no_sobrescribe(self):
        self.crear("Caso repetido")
        with self.assertRaises(nc.ErrorDeCaso):
            self.crear("Caso repetido")

    def test_materia_inexistente(self):
        with self.assertRaises(nc.ErrorDeCaso):
            self.crear(materia="no-existe")

    def test_slugify(self):
        self.assertEqual(nc.slugify("Acción de tutela — Salud"), "accion-de-tutela-salud")
        self.assertEqual(nc.slugify("   "), "caso")

    def test_crea_caso_de_demanda_laboral(self):
        shutil.copytree(RAIZ / "materias" / "demanda-laboral", self.tmp / "materias" / "demanda-laboral")
        r = self.crear("Demanda de prueba", materia="demanda-laboral", area="laboral")
        self.assertEqual(r["materia"], "demanda-laboral")
        expediente = (self.tmp / "casos" / "demanda-de-prueba" / "00-expediente.md").read_text(encoding="utf-8")
        self.assertIn("materias/demanda-laboral/plantillas/modelo-demanda-laboral.md", expediente)
        self.assertIn("fuentes/02_laboral", expediente)

    def test_director_personalizado(self):
        self.crear("Caso con director", director="Jorge", trato="usted",
                   titulo="Doctor", estilo="cercano", presentacion="breve")
        expediente = (self.tmp / "casos" / "caso-con-director" / "00-expediente.md").read_text(encoding="utf-8")
        for texto in ("Jorge", "usted", "Doctor", "cercano", "breve"):
            self.assertIn(texto, expediente)
        self.assertNotIn("{{", expediente)


class TestExpedientesExistentes(unittest.TestCase):
    """Los expedientes de ejemplo deben apuntar a archivos que existen."""

    CAMPOS = ("Entrada", "Plantilla", "Checklist", "Plazos", "Corpus")

    def test_cada_expediente_apunta_a_archivos_reales(self):
        for ruta in sorted((RAIZ / "casos").glob("*/00-expediente.md")):
            texto = ruta.read_text(encoding="utf-8")
            for campo in self.CAMPOS:
                m = re.search(rf"\| {campo} \| `([^`]+)`", texto)
                if not m:
                    continue
                valor = m.group(1)
                if "{{" in valor:
                    continue
                for parte in valor.split(","):
                    parte = parte.strip().strip("`")
                    if not parte or parte.startswith("NO CONSTA"):
                        continue
                    # Unas rutas son relativas a la raíz (plantilla, materia, corpus)
                    # y otras a la carpeta del caso (entrada, hechos, borrador).
                    existe = (RAIZ / parte).exists() or (ruta.parent / parte).exists()
                    self.assertTrue(existe, f"{ruta}: no existe {campo}={parte}")


if __name__ == "__main__":
    unittest.main()
