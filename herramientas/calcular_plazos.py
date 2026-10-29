#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Herramienta Determinística de Cálculo de Plazos — Despacho Pessoa
=================================================================
Regla 5 del Estatuto: "Plazos con herramienta determinística, nunca con el modelo."

Calcula términos en días hábiles de Colombia (excluye sábados, domingos y festivos).
Los festivos se leen de herramientas/festivos_colombia.json (Ley 51 de 1983); solo hay
cálculo para los años cargados en ese archivo (hoy 2026 y 2027). Si la fecha de inicio,
la de corte o el vencimiento caen en un año sin festivos, la herramienta se niega a
calcular en vez de contar mal.

Modos soportados:
  - peticion          : 15 días hábiles (Art. 14 Ley 1755 de 2015 / Art. 16 Ley 1266 de 2008)
  - peticion_docs     : 10 días hábiles (Art. 14 núm. 1 Ley 1755 de 2015)
  - peticion_consulta : 30 días hábiles (Art. 14 núm. 2 Ley 1755 de 2015)
  - fallo_tutela      : 10 días hábiles (Art. 86 CP y Art. 29 Decreto 2591 de 1991)
  - impugnacion       : 3 días hábiles (Art. 31 Decreto 2591 de 1991)
  - cumplimiento_48h  : 48 HORAS corridas (Art. 27 Decreto 2591 de 1991); no son 2 días hábiles

Regla de cómputo (Art. 62 Ley 4 de 1913 / CGP Art. 118):
  El conteo de días hábiles inicia el primer día hábil SIGUIENTE a la radicación o notificación.

La herramienta solo calcula fechas; no emite conclusiones jurídicas.

Ejemplos de uso:
  python herramientas/calcular_plazos.py --modo peticion --fecha-inicio 2026-09-25 --fecha-actual 2026-10-30
  python herramientas/calcular_plazos.py --modo cumplimiento_48h --fecha-inicio 2026-10-09
  python herramientas/calcular_plazos.py --demo-casos
"""

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path
import sys

RUTA_FESTIVOS = Path(__file__).resolve().parent / "festivos_colombia.json"


def fecha_de_hoy() -> date:
    """Fecha de corte por defecto: el día en que se ejecuta el despacho."""
    return date.today()


class ErrorDeEntrada(ValueError):
    """Entrada que la calculadora no puede procesar con honestidad."""


def cargar_festivos(ruta: Path = RUTA_FESTIVOS) -> tuple[dict, set]:
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        festivos, años = {}, set()
        for año, dias in datos.items():
            if año.startswith("_"):
                continue
            años.add(int(año))
            for iso, nombre in dias.items():
                f = date.fromisoformat(iso)
                if f.year != int(año):
                    raise ErrorDeEntrada(f"La fecha {iso} está bajo el año {año} en {ruta.name}.")
                festivos[f] = nombre
    except ErrorDeEntrada:
        raise
    except (OSError, ValueError, AttributeError, TypeError) as exc:
        raise ErrorDeEntrada(
            f"No pude leer el archivo de festivos {ruta.name}: {exc}. Revisa su formato (JSON con años y fechas ISO).") from exc
    return festivos, años


try:
    FESTIVOS, AÑOS_CARGADOS = cargar_festivos()
    ERROR_CARGA_FESTIVOS = None
except ErrorDeEntrada as _exc:  # main() lo reporta y sale con código 2
    FESTIVOS, AÑOS_CARGADOS = {}, set()
    ERROR_CARGA_FESTIVOS = str(_exc)

# (cantidad, descripción, unidad)
MODOS_PLAZO = {
    "peticion": (15, "Derecho de Petición General / Reclamo Habeas Data (Art. 14 Ley 1755 de 2015 / Art. 16 Ley 1266 de 2008)", "habiles"),
    "peticion_docs": (10, "Petición de Documentos e Información / Historia Clínica (Art. 14 núm. 1 Ley 1755 de 2015)", "habiles"),
    "peticion_consulta": (30, "Petición de Consulta (Art. 14 núm. 2 Ley 1755 de 2015)", "habiles"),
    "fallo_tutela": (10, "Término para fallar Acción de Tutela (Art. 86 CP / Art. 29 Decreto 2591 de 1991)", "habiles"),
    "impugnacion": (3, "Término para impugnar el fallo de tutela (Art. 31 Decreto 2591 de 1991)", "habiles"),
    "cumplimiento_48h": (48, "Cumplimiento de orden de tutela en 48 horas (Art. 27 Decreto 2591 de 1991)", "horas"),
}


def validar_fechas(fecha_inicio: date, fecha_actual: date) -> None:
    for f in (fecha_inicio, fecha_actual):
        if f.year not in AÑOS_CARGADOS:
            raise ErrorDeEntrada(
                f"No tengo festivos cargados para el año {f.year}. Años disponibles: "
                f"{', '.join(map(str, sorted(AÑOS_CARGADOS)))}. Añádelos en herramientas/festivos_colombia.json.")
    if fecha_inicio > fecha_actual:
        raise ErrorDeEntrada(
            f"La fecha de inicio ({fecha_inicio}) es posterior a la fecha de corte ({fecha_actual}). Revisa las fechas.")


def calcular_vencimiento_horas(fecha_inicio: date, horas: int) -> dict:
    """Plazo en horas corridas desde la notificación. Sin hora exacta, el vencimiento es el mismo
    momento del día horas/24 días después."""
    if horas % 24:
        raise ErrorDeEntrada(
            "esta herramienta solo cuenta plazos en horas que sean múltiplos de 24; "
            "para otros usa fecha y hora exactas")
    venc = fecha_inicio + timedelta(hours=horas)
    if venc.year not in AÑOS_CARGADOS:
        raise ErrorDeEntrada(
            f"El plazo cruza al año {venc.year} y no tengo sus festivos. "
            "Añádelos en herramientas/festivos_colombia.json.")
    return {"fecha_inicio": fecha_inicio, "horas": horas, "fecha_vencimiento": venc,
            "nota": ("Plazo en horas corridas. Si la orden fija otra forma de contar, prevalece la orden. "
                     "El estado tiene granularidad de día (no se compara la hora).")}


DIAS_SEMANA_ES = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}


def es_dia_habil(d: date) -> tuple[bool, str]:
    """Determina si una fecha es día hábil en Colombia y devuelve el motivo si no lo es."""
    if d.weekday() == 5:
        return False, "Sábado (inhábil)"
    if d.weekday() == 6:
        return False, "Domingo (inhábil)"
    if d in FESTIVOS:
        return False, f"Festivo en Colombia: {FESTIVOS[d]}"
    return True, "Día hábil"


def calcular_vencimiento(fecha_inicio: date, dias_habiles_objetivo: int) -> dict:
    """
    Calcula la fecha exacta de vencimiento sumando `dias_habiles_objetivo`
    a partir del día siguiente a `fecha_inicio`.
    """
    if dias_habiles_objetivo < 1:
        raise ErrorDeEntrada("el número de días hábiles debe ser al menos 1")
    if fecha_inicio.year not in AÑOS_CARGADOS:
        raise ErrorDeEntrada(f"No tengo festivos cargados para el año {fecha_inicio.year}.")
    cursor = fecha_inicio
    conteo_habiles = 0
    calendario_detalle = []
    festivos_cruzados = []

    while conteo_habiles < dias_habiles_objetivo:
        cursor += timedelta(days=1)
        if cursor.year not in AÑOS_CARGADOS:
            raise ErrorDeEntrada(
                f"El plazo cruza al año {cursor.year} y no tengo sus festivos. "
                "Añádelos en herramientas/festivos_colombia.json.")
        habil, motivo = es_dia_habil(cursor)
        if habil:
            conteo_habiles += 1
            calendario_detalle.append(
                f"  Día hábil #{conteo_habiles:02d}: {cursor.isoformat()} ({DIAS_SEMANA_ES[cursor.weekday()]})"
            )
        else:
            if cursor in FESTIVOS:
                festivos_cruzados.append(f"{cursor.isoformat()} ({FESTIVOS[cursor]})")

    return {
        "fecha_inicio": fecha_inicio,
        "dias_habiles_objetivo": dias_habiles_objetivo,
        "fecha_vencimiento": cursor,
        "calendario_detalle": calendario_detalle,
        "festivos_cruzados": festivos_cruzados,
    }


def contar_dias_habiles_transcurridos(fecha_inicio: date, fecha_actual: date) -> dict:
    """Cuenta cuántos días hábiles y calendario han transcurrido entre fecha_inicio (excluida) y fecha_actual (incluida)."""
    if fecha_actual <= fecha_inicio:
        return {
            "habiles_transcurridos": 0,
            "calendario_transcurridos": (fecha_actual - fecha_inicio).days,
            "festivos_en_rango": [],
        }

    cursor = fecha_inicio
    habiles = 0
    festivos = []
    while cursor < fecha_actual:
        cursor += timedelta(days=1)
        habil, _ = es_dia_habil(cursor)
        if habil:
            habiles += 1
        elif cursor in FESTIVOS:
            festivos.append(f"{cursor.isoformat()} ({FESTIVOS[cursor]})")

    return {
        "habiles_transcurridos": habiles,
        "calendario_transcurridos": (fecha_actual - fecha_inicio).days,
        "festivos_en_rango": festivos,
    }


def imprimir_reporte(
    modo: str,
    fecha_inicio: date,
    fecha_actual: date,
    dias_personalizados: int | None = None,
    mostrar_detalle: bool = True,
    corte_por_defecto: bool = False,
) -> None:
    validar_fechas(fecha_inicio, fecha_actual)
    cantidad, descripcion, unidad = MODOS_PLAZO[modo]
    if dias_personalizados is not None:
        cantidad, unidad = dias_personalizados, "habiles"
        descripcion = f"Plazo personalizado de {cantidad} días hábiles"

    etiqueta_corte = " (fecha de referencia por defecto)" if corte_por_defecto else ""
    titulo = (f"CALCULADORA DETERMINÍSTICA DE PLAZOS — DESPACHO PESSOA "
              f"(COLOMBIA, festivos {min(AÑOS_CARGADOS)}-{max(AÑOS_CARGADOS)})")
    cabecera = [
        f"Norma / Modo aplicado     : {descripcion}",
        f"Fecha de radicación/hito  : {fecha_inicio.isoformat()} ({DIAS_SEMANA_ES[fecha_inicio.weekday()]})",
        f"Fecha de corte / consulta : {fecha_actual.isoformat()} ({DIAS_SEMANA_ES[fecha_actual.weekday()]}){etiqueta_corte}",
    ]

    if unidad == "horas":
        res = calcular_vencimiento_horas(fecha_inicio, cantidad)
        venc = res["fecha_vencimiento"]
        if fecha_actual > venc:
            estado = "VENCIDO (el término se cumplió antes de la fecha de corte)"
        elif fecha_actual == venc:
            estado = "EN CURSO — vence hoy, a la hora de la notificación"
        else:
            estado = "EN CURSO"
        print("=" * 78)
        print(titulo)
        print("=" * 78)
        for linea in cabecera:
            print(linea)
        print(f"Término exigido           : {cantidad} horas corridas")
        print("-" * 78)
        print(f"FECHA EXACTA VENCIMIENTO  : {venc.isoformat()} ({DIAS_SEMANA_ES[venc.weekday()]}) a la misma hora de la notificación")
        print(f"ESTADO DEL TÉRMINO        : {estado}")
        print(f"Nota                      : {res['nota']}")
        print("=" * 78)
        return

    resultado = calcular_vencimiento(fecha_inicio, cantidad)
    transcurrido = contar_dias_habiles_transcurridos(fecha_inicio, fecha_actual)
    fecha_venc = resultado["fecha_vencimiento"]

    if fecha_actual > fecha_venc:
        estado = "VENCIDO (el término se cumplió antes de la fecha de corte)"
    elif fecha_actual == fecha_venc:
        estado = "EN CURSO — vence hoy"
    else:
        faltan = cantidad - transcurrido["habiles_transcurridos"]
        estado = f"EN CURSO — faltan {faltan} día(s) hábil(es)"

    print("=" * 78)
    print(titulo)
    print("=" * 78)
    for linea in cabecera:
        print(linea)
    print(f"Término exigido           : {cantidad} días hábiles")
    print("Regla de cómputo          : inicia el día hábil siguiente a la radicación (Art. 62 Ley 4ª de 1913; CGP art. 118) [referencia de la herramienta: no es cita del corpus]")
    habil_inicio, motivo_inicio = es_dia_habil(fecha_inicio)
    if not habil_inicio:
        print(f"AVISO: la fecha de radicación es inhábil ({motivo_inicio}). Esta calculadora cuenta desde el primer día "
              "hábil siguiente; si el despacho la tiene por recibida el siguiente día hábil, el vencimiento corre un día más. "
              "Decisión del abogado.")
    print(
        f"Festivos en el período    : {', '.join(resultado['festivos_cruzados']) if resultado['festivos_cruzados'] else 'Ninguno'}"
    )
    print("-" * 78)
    print(
        f"FECHA EXACTA VENCIMIENTO  : {fecha_venc.isoformat()} ({DIAS_SEMANA_ES[fecha_venc.weekday()]}) — vence en esta fecha"
    )
    print(
        f"Días transcurridos al corte: {transcurrido['habiles_transcurridos']} días hábiles ({transcurrido['calendario_transcurridos']} días calendario)"
    )
    print(f"ESTADO DEL TÉRMINO        : {estado}")
    print("Nota: la hora límite depende del canal y del despacho (CGP art. 109); esta herramienta cuenta fechas, no horas. [referencia de la herramienta: no es cita del corpus]")
    print("-" * 78)

    if mostrar_detalle:
        print("Desglose día a día hábil (el conteo inicia el día hábil siguiente a la radicación):")
        for linea in resultado["calendario_detalle"]:
            print(linea)
        print("=" * 78)


def ejecutar_demo_casos() -> None:
    fecha_hoy = fecha_de_hoy()
    print(f"\n>>> DEMOSTRACIÓN AUTOMÁTICA DE PLAZOS (fecha de referencia: {fecha_hoy.isoformat()})\n")

    print("[PETICION] Derecho de petición radicado el 2026-09-25:")
    imprimir_reporte("peticion", date(2026, 9, 25), fecha_hoy, mostrar_detalle=False)

    print(f"\n[DIAS TRANSURRIDOS] Desde el 2026-10-05 hasta el {fecha_hoy.isoformat()}:")
    trans = contar_dias_habiles_transcurridos(date(2026, 10, 5), fecha_hoy)
    print(
        f"  -> {trans['calendario_transcurridos']} días calendario "
        f"({trans['habiles_transcurridos']} días hábiles). "
        "La valoración de inmediatez corresponde al abogado, no a esta calculadora."
    )

    print("\n[PETICION] Reclamo radicado el 2026-10-08:")
    imprimir_reporte("peticion", date(2026, 10, 8), fecha_hoy, mostrar_detalle=True)


def parse_date(s: str) -> date:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Fecha inválida '{s}'. Usa el formato ISO YYYY-MM-DD (ej. 2026-10-30)."
        ) from exc


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    if ERROR_CARGA_FESTIVOS:
        print(f"No puedo calcular: {ERROR_CARGA_FESTIVOS}")
        return 2

    parser = argparse.ArgumentParser(
        description="Calculadora determinística de plazos procesales y de tutela en Colombia (festivos en festivos_colombia.json)."
    )
    parser.add_argument(
        "--modo",
        choices=list(MODOS_PLAZO.keys()),
        default="peticion",
        help="Tipo de término legal a calcular (por defecto: peticion = 15 días hábiles).",
    )
    parser.add_argument(
        "--fecha-inicio",
        type=parse_date,
        help="Fecha de radicación o notificación en formato YYYY-MM-DD.",
    )
    parser.add_argument(
        "--fecha-actual",
        type=parse_date,
        default=None,
        help="Fecha de corte para verificar estado (por defecto: hoy).",
    )
    parser.add_argument(
        "--dias",
        type=int,
        default=None,
        help="Opcional: número personalizado de días hábiles a contar.",
    )
    parser.add_argument(
        "--sin-detalle",
        action="store_true",
        help="Omitir la lista detallada de cada día hábil.",
    )
    parser.add_argument(
        "--demo-casos",
        action="store_true",
        help="Ejecuta un cálculo demostrativo de plazos.",
    )

    args = parser.parse_args()

    if args.demo_casos:
        ejecutar_demo_casos()
        return 0

    if not args.fecha_inicio:
        parser.error("Debes indicar --fecha-inicio YYYY-MM-DD o usar --demo-casos.")

    if args.dias is not None and args.dias < 1:
        print("No puedo calcular: el número de días hábiles debe ser al menos 1.")
        return 2

    corte_por_defecto = args.fecha_actual is None
    fecha_actual = fecha_de_hoy() if corte_por_defecto else args.fecha_actual
    try:
        imprimir_reporte(
            modo=args.modo,
            fecha_inicio=args.fecha_inicio,
            fecha_actual=fecha_actual,
            dias_personalizados=args.dias,
            mostrar_detalle=not args.sin_detalle,
            corte_por_defecto=corte_por_defecto,
        )
    except ErrorDeEntrada as e:
        print(f"No puedo calcular: {e}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
