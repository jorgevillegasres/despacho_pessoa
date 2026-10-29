# Expediente {{ID}} — {{NOMBRE}}

> **Esta carátula es lo primero que lee cada agente.** De aquí saca la materia, el tipo de documento, la plantilla, el corpus y las rutas de entrada y salida. Si un campo no aplica, escribe `NO CONSTA`.

## 0. Director

| Campo | Valor |
|---|---|
| Cómo llamarlo | {{DIRECTOR}} |
| Trato | {{TRATO}} |
| Título | {{TITULO}} |
| Estilo | {{ESTILO}} |
| Presentación | {{PRESENTACION}} |

## 1. Identificación

| Campo | Valor |
|---|---|
| ID | {{ID}} |
| Nombre | {{NOMBRE}} |
| Materia | {{MATERIA}} |
| Área | {{AREA}} |
| Tipo de documento | {{TIPO_DOCUMENTO}} |
| Cliente / usuario | {{CLIENTE}} |
| Parte contraria | {{PARTE_CONTRARIA}} |
| Responsable | {{RESPONSABLE}} |
| Supervisor | {{SUPERVISOR}} |
| Nivel de confidencialidad | {{CONFIDENCIALIDAD}} |
| Fecha de apertura | {{FECHA_APERTURA}} |
| Estado | abierto |

## 2. Rutas del caso

| Campo | Valor |
|---|---|
| Entrada | `01-entrada/entrevista-y-pruebas.md` |
| Pruebas | `01-entrada/pruebas/` |
| Hechos | `02-hechos/hechos.md` |
| Investigación | `03-investigacion/investigacion.md` |
| Fichas | `03-investigacion/fichas/` |
| Borrador | `04-borrador/borrador.md` |
| Verificación | `05-auditoria/informe-verificacion.md` |
| Riesgo | `05-auditoria/informe-riesgo.md` |
| Decisión | `06-decision/decision.md` |
| Registro | `06-decision/registro-ejecucion.md` |
| Plantilla | `{{PLANTILLA}}` |
| Checklist | `{{CHECKLIST}}` |
| Plazos | `{{PLAZOS}}` |
| Corpus | `{{CORPUS}}` |

## 3. Materia

| Campo | Valor |
|---|---|
| Materia | `{{MATERIA}}` |
| Archivo de configuración | `materias/{{MATERIA}}/materia.json` |
| Tipo de documento | {{TIPO_DOCUMENTO}} |

> Si el expediente y la materia se contradicen, prevalece el expediente. Si falta un dato, escribe `NO CONSTA` y pide la decisión del Socio Director.

## 4. Estado y plazos

| Campo | Valor |
|---|---|
| Próximo plazo | `NO CONSTA` |
| Próxima acción | Entrevista y recolección de pruebas |
| Fecha de cierre | `NO CONSTA` |

## 5. Checklist

- [ ] Entrevista
- [ ] Pruebas
- [ ] Matriz de hechos
- [ ] Investigación y fichas
- [ ] Borrador
- [ ] Verificación
- [ ] Riesgo
- [ ] Decisión
- [ ] Firma

## 6. Registro

| Fecha | Etapa | Agente | Archivo | Decisión |
|---|---|---|---|---|
| {{FECHA_APERTURA}} | Apertura | Sistema | `00-expediente.md` | Caso creado |
