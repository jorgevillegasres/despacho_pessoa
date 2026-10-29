# Ficha de Cita Jurídica — Despacho Pessoa

> **Regla 2 del Estatuto:** Toda norma o sentencia que pretenda incluirse en el borrador de tutela debe contar previamente con esta ficha completa en `investigacion.md`. El Redactor (*Ricardo Reis*) tiene prohibido invocar normas o fallos sin ficha, y el Verificador (*Bernardo Soares*) declarará `NO COINCIDE` cualquier cita que se aparte del extracto textual aquí consignado, y `FUERA DEL CORPUS` la que no esté en `fuentes/`.

---

## Estructura de la Ficha

```markdown
### FICHA-[NÚMERO]: [Identificador corto, ej. Art. 86 Constitución Política / Sentencia SU-508 de 2020]
- **Tipo de fuente:** [Constitución / Ley Estatutaria / Decreto / Sentencia de Unificación / Sentencia de Revisión]
- **Archivo en el corpus (`fuentes/`):** `[Ruta exacta relativa, ej. fuentes/01_salud/corte_const_SU-508_2020_suministros.md]`
- **Ubicación exacta dentro del archivo:** `[Artículo, numeral, parágrafo o sección exacta del documento]`
- **Enlace oficial de referencia:** `[URL oficial incluida en el encabezado del archivo de fuentes/]`
- **Cita textual literal (entre comillas):**
  > "[Copiar y pegar letra por letra el fragmento exacto que obra en el archivo de fuentes/. Prohibido parafrasear en este campo.]"
- **Hecho(s) del caso al que se aplica:** `[Referencia al numeral de hechos.md, ej. HECHO-03, HECHO-05]`
- **Pertinencia jurídica breve:** `[Explicación de 1 a 2 líneas de por qué esta cita resuelve el punto jurídico sin extralimitar lo que dice el texto]`
```

---

## Lista de Chequeo antes de Aprobar la Ficha
1. ¿El archivo indicado en `Archivo en el corpus` existe realmente en la carpeta `fuentes/`?
2. ¿La `Cita textual literal` coincide palabra por palabra con el contenido del archivo?
3. ¿El hecho al que se vincula está clasificado como **PROBADO** en `hechos.md` (y no como `NO CONSTA`)?
