# Checklist — Acción de tutela

> **Uso:** el Redactor y el Verificador la usan como lista de control. No sustituye la revisión del abogado. Verifica la norma vigente y el caso concreto.

## 1. Procedencia

- [ ] ¿El derecho invocado es fundamental?
- [ ] ¿Existe una acción u omisión que lo vulnere o amenace?
- [ ] ¿La entidad o el particular es demandable? (legitimación por pasiva)
- [ ] ¿El titular está legitimado? (legitimación por activa; agencia oficiosa si aplica)
- [ ] ¿Se cumplen los requisitos de inmediatez? (tiempo transcurrido y razones)
- [ ] ¿Se agotaron los medios ordinarios o se configura una excepción? (subsidiariedad)
- [ ] La subsidiariedad sigue un solo camino: o el otro medio no es idóneo ni eficaz en concreto (tutela como mecanismo definitivo), o sí lo es pero hay perjuicio irremediable (tutela como mecanismo transitorio). No se mezclan los dos. (Art. 6 num. 1 y art. 8 del Decreto 2591 de 1991; en salud, SU-508 de 2020 y SU-239 de 2024 en `fuentes/01_salud/`.)
- [ ] ¿Hay perjuicio irremediable? (solo si se invoca la tutela como mecanismo transitorio)
- [ ] Si el accionado es un particular, ¿está acreditada la causal del art. 42 del Decreto 2591 de 1991 (servicio público de salud, subordinación o indefensión, habeas data)? Texto completo en `fuentes/00_transversal/decreto_2591_de_1991_arts_7_42_medidas_provisionales_y_particulares.md`.
- [ ] Si actúa agente oficioso, ¿consta la manifestación de actuar en esa calidad y una prueba, al menos sumaria, de la imposibilidad del titular? (Art. 10 del Decreto 2591 de 1991 y `fuentes/00_transversal/corte_const_agencia_oficiosa_T-382_2021_T-046_2026.md`.)
- [ ] Si los hechos muestran un riesgo actual, ¿se pide medida provisional? (Art. 7 del Decreto 2591 de 1991.)

## 2. Hechos y pruebas

- [ ] Cada hecho tiene fecha, descripción y prueba.
- [ ] Los hechos dudosos están marcados `NO CONSTA`.
- [ ] Las pruebas están inventariadas y son pertinentes.
- [ ] Las afirmaciones del cliente que contradicen documentos están identificadas.
- [ ] Los plazos se calcularon con `herramientas/calcular_plazos.py`.

## 3. Fundamento jurídico

- [ ] Cada norma o sentencia tiene ficha de cita.
- [ ] La cita textual es literal y está ubicada.
- [ ] La ratio decidendi está identificada como regla.
- [ ] El precedente es aplicable o se explica el *distinguishing*.
- [ ] No se cita nada que esté fuera del corpus.

## 4. Escrito

- [ ] Encabezado y destinatario.
- [ ] Legitimación activa y pasiva.
- [ ] Hechos en orden cronológico.
- [ ] Procedencia (inmediatez, subsidiariedad, perjuicio).
- [ ] Fundamentos de derecho y concepto de la violación.
- [ ] Pretensiones claras y viables.
- [ ] Pruebas y anexos numerados.
- [ ] Juramento (art. 37 Decreto 2591 de 1991).
- [ ] Notificaciones.
- [ ] Firma del supervisor.

## 5. Términos

- [ ] 10 días hábiles para fallar (art. 86 CP / art. 29 Decreto 2591 de 1991).
- [ ] 3 días hábiles para impugnar (art. 31 Decreto 2591 de 1991).
- [ ] 48 horas para cumplimiento (art. 27 Decreto 2591 de 1991), si aplica.
- [ ] Cualquier otro término: verificar en la norma y calcular con la herramienta.

## 6. Cierre

- [ ] El informe de verificación está en `05-auditoria/`.
- [ ] El informe de riesgo está en `05-auditoria/`.
- [ ] El Director registró su decisión en `06-decision/`.
- [ ] El supervisor revisó y firmó.
