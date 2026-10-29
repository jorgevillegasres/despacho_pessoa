# Bitácora de Ejecuciones - Despacho Pessoa (`registro.md`)

> **Regla de Auditoría (Estatuto, Reglas 4 y 6):** Todo paso ejecutado por un agente o herramienta determinística debe quedar asentado en esta bitácora con fecha, caso, agente interviniente, archivos leídos, archivo producido y decisión del Socio Director (humano).

---

## Tabla de Registro Auditable

| Fecha y Hora | Caso | Rol / Agente | Entradas Leídas | Salida Generada | Hallazgos / Alertas Clave | Estado / Firma Socio Director |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|  |  |  |  |  |  |  |

Esta tabla empieza vacía. Añade una fila por cada ejecución o pega un «Asiento de Auditoría» con la plantilla de abajo.

---

## Plantilla para Nuevos Asientos (Copiar y Pegar al final)

```markdown
### Asiento de Auditoría - [Caso] - [Fecha]
- **Agente / Herramienta:**
- **Archivos de entrada:**
- **Archivo de salida:**
- **Verificación de Reglas del Estatuto:**
  - [ ] ¿Respetó el corpus cerrado `fuentes/`?
  - [ ] ¿Marcó `NO CONSTA` ante vacíos probatorios?
  - [ ] ¿Usó `calcular_plazos.py` para conteo de términos?
  - [ ] ¿`verificar_corpus.py --comprobar` dio «intacto» antes y después?
  - [ ] ¿`verificar_citas.py` aprobó el borrador?
  - [ ] Leyó `informe-verificacion.md` e `informe-riesgo.md` completos (Regla 6)
- **Decisión del Socio Director:** [APROBADO / DEVUELTO A REDACTOR / DESCARTADO]
- **Observaciones del Socio Director:**
```

### Asiento de Auditoría - Biblioteca (corpus) - 2026-10-29
- **Agente / Herramienta:** Socio Director, con el conector GMH LEX (buscar_jurisprudencia, buscar_normas, obtener_articulo, metodo_gmh) y `herramientas/verificar_corpus.py --sellar`.
- **Archivos de entrada:** resultados del conector GMH LEX del 2026-10-29 (fragmentos de providencias con enlace al PDF; artículos 7 y 42 del Decreto 2591 de 1991; artículos 61 y 63 de la Ley 2452 de 2025).
- **Archivo de salida:** diez archivos nuevos en `fuentes/` (cuatro en `00_transversal/`, dos en `01_salud/`, tres en `02_laboral/`, uno en `03_habeas_data/`), diez filas nuevas en `fuentes/00-indice.md` y nuevo `fuentes/SELLO.json` (26 archivos).
- **Verificación de Reglas del Estatuto:**
  - [x] ¿Respetó el corpus cerrado `fuentes/`? Las fuentes nuevas traen solo texto devuelto por el conector, con su enlace; nada de memoria.
  - [x] ¿Marcó `NO CONSTA` ante vacíos probatorios? No aplica (no es un caso).
  - [x] ¿Usó `calcular_plazos.py` para conteo de términos? No aplica.
  - [x] ¿`verificar_corpus.py --comprobar` dio «intacto» antes y después? Sí: 16 archivos antes, 26 después del nuevo sello.
  - [ ] ¿`verificar_citas.py` aprobó el borrador? No aplica.
  - [ ] Leyó `informe-verificacion.md` e `informe-riesgo.md` completos (Regla 6). No aplica.
- **Decisión del Socio Director:** [PENDIENTE DE FIRMA] Las diez fuentes quedan en estado «Consulta registrada»: el cotejo letra por letra contra el sitio oficial sigue pendiente.
- **Observaciones del Socio Director:**
