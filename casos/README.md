# Casos

Esta carpeta reúne los expedientes del despacho. **El sistema no incluye casos precargados.** Solo están la plantilla y el índice vacío para que crees el tuyo.

## Crear un caso

```text
python herramientas/nuevo_caso.py
```

El script copia `casos/_PLANTILLA-CASO/` en `casos/<tu-caso>/`, reemplaza los marcadores `{{...}}` y añade una fila a `casos/00-indice.md`. También puedes copiar la plantilla a mano:

```text
cp -r casos/_PLANTILLA-CASO casos/mi-primer-caso
```

y completar la carátula.

## Qué hay dentro de un caso

```text
casos/<tu-caso>/
├── 00-expediente.md              # materia, corpus, rutas, Director
├── 01-entrada/
│   ├── entrevista-y-pruebas.md   # relato del cliente e inventario de pruebas
│   └── pruebas/                  # documentos del expediente
├── 02-hechos/hechos.md           # salida de Caeiro
├── 03-investigacion/             # salida de Search
├── 04-borrador/                  # salida de Reis
├── 05-auditoria/                 # informes de Soares y Campos
├── 06-decision/                  # tu decisión y el registro del caso
└── 07-archivo/
```

La **entrada** es lo único que ve el primer agente: el relato y las pruebas, sin conclusiones jurídicas. Todo lo que no conste se marca `NO CONSTA`. El **expediente** dice qué materia usa el caso, qué plantilla sigue, qué corpus lee y quién responde.

## Reglas de la carpeta

- Un caso, una carpeta. El nombre se escribe en minúsculas y con guiones: `mi-primer-caso`.
- Los datos de personas, cédulas, radicados y empresas deben ser ficticios o estar anonimizados.
- No agregues conclusiones jurídicas en `01-entrada/`: eso es trabajo de los agentes.
- Las salidas de los agentes (`hechos.md`, `investigacion.md`, `borrador.md`, `informe-*.md`) están ignoradas por git para que no se publiquen por accidente. Si quieres versionar las tuyas, usa `git add -f` o ajusta tu copia de `.gitignore`.
- Si quieres guardar notas internas del despacho, usa `casos/<tu-caso>/privado/`, que está ignorada.

## Después de crear el caso

1. Completa `00-expediente.md`.
2. Escribe `01-entrada/entrevista-y-pruebas.md`.
3. Añade las pruebas a `01-entrada/pruebas/`.
4. Ejecuta los agentes en orden. Las guías están en [`docs/guias/`](../docs/guias/).
5. Decide y firma en `06-decision/decision.md` y `registro.md`.
