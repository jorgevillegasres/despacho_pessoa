# Índice de casos

> **Tablero del despacho.** Una fila por caso. Esta versión no trae casos precargados: crea el primero con `python herramientas/nuevo_caso.py` o copia `casos/_PLANTILLA-CASO/`.

| ID | Caso | Materia | Area | Cliente / usuario | Estado | Próximo plazo | Responsable | Última actualización |
|---|---|---|---|---|---|---|---|---|
<!-- CASOS-NUEVOS -->

## Cómo leer el índice

- **Estado:** abierto / en revisión / cerrado / archivado.
- **Próximo plazo:** la fecha más próxima que el expediente registre; si no consta, `Ver expediente`.
- **Responsable:** el abogado o responsable del caso.
- **Última actualización:** la fecha del último asiento en el registro del caso.

## Regla

El índice es una vista. La fuente de verdad es `casos/<caso>/00-expediente.md`. Si hay contradicción, prevalece el expediente.
