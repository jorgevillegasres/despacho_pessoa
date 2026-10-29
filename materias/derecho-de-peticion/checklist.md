# Checklist — Derecho de petición

> **Uso:** lista de control para el Redactor y el Verificador. No sustituye la revisión del abogado. Verifica la norma vigente y el caso concreto. Los puntos marcados «verificar» vienen del método de redacción consultado en GMH LEX y señalan reglas cuyo artículo todavía no está en el corpus: no se citan hasta incorporarlo.

## 1. Destinatario y modalidad

- [ ] ¿El destinatario es la autoridad o el particular que puede resolver lo pedido, con el cargo o la dependencia?
- [ ] Si el destinatario es un particular (EPS, empleador, banco, operador de datos), ¿el corpus respalda que procede la petición contra él? (Art. 32 Ley 1755 de 2015, en `fuentes/00_transversal/`.)
- [ ] ¿El escrito dice desde la primera línea qué modalidad ejerce (información, copias, consulta, queja, reclamo, petición en interés particular o general)? De la modalidad depende el término. (Art. 13 Ley 1755 de 2015.)
- [ ] «Verificar»: si se dirige a quien no es competente, la norma prevé la remisión; el término correría desde que la recibe la autoridad competente. Artículo por incorporar al corpus antes de citarlo.

## 2. Peticionario

- [ ] Identificación completa, dirección física y correo electrónico para notificaciones.
- [ ] Si actúa apoderado o agente oficioso, poder o constancia de la calidad en que actúa.
- [ ] Si el peticionario es sujeto de especial protección (adulto mayor, persona con discapacidad, menor, gestante, persona en debilidad manifiesta), ¿el escrito lo dice y lo apoya en un hecho probado? «Verificar» la norma de atención preferente antes de citarla.

## 3. Hechos y pruebas

- [ ] Hechos breves, numerados, solo los necesarios para que el destinatario entienda qué se pide y por qué le corresponde.
- [ ] Cada hecho tiene fecha, descripción y prueba (`[Fuente: HECHO-XX de hechos.md — Prueba P-YY]`).
- [ ] Los hechos dudosos están marcados `NO CONSTA`.
- [ ] Si ya hubo una petición anterior, están su fecha de radicación y la respuesta (o la falta de respuesta) como hechos probados.

## 4. Peticiones

- [ ] Numeradas, una por punto, de modo que cada una pueda responderse por separado.
- [ ] Concretas: nada de «toda la información relacionada con».
- [ ] Solo pide lo que un hecho probado y una ficha sustentan.

## 5. Fundamentos

- [ ] Art. 23 de la Constitución y Ley 1755 de 2015, con ficha de cita (`fuentes/00_transversal/constitucion_art_23_86.md` y `fuentes/00_transversal/ley_1755_de_2015_peticion.md`).
- [ ] Qué cuenta como respuesta de fondo (clara, precisa, congruente, consecuente, notificada): ficha de `fuentes/00_transversal/corte_const_derecho_de_peticion_respuesta_de_fondo_T-329_2021_T-197_2024.md`.
- [ ] Cada regla invocada tiene artículo o radicado y ficha de cita. Nada fuera del corpus.
- [ ] Si es un reclamo de habeas data, los artículos 12 y 16 de la Ley 1266 de 2008 están en `fuentes/03_habeas_data/`.

## 6. Término de respuesta

- [ ] Sección propia y corta con el término que aplica a la modalidad: 15 días hábiles (regla general), 10 (documentos e información) o 30 (consultas). Art. 14 Ley 1755 de 2015.
- [ ] En la modalidad de documentos e información, el escrito advierte lo que dice el art. 14 num. 1 sobre el silencio: la solicitud se entiende aceptada y las copias se entregan en los tres días siguientes.
- [ ] El plazo se calculó con `herramientas/calcular_plazos.py` (modo `peticion`, `peticion_docs` o `peticion_consulta`). Nunca de cabeza.

## 7. Escrito

- [ ] Destinatario con cargo.
- [ ] Identificación del peticionario.
- [ ] Objeto y modalidad.
- [ ] Hechos.
- [ ] Peticiones.
- [ ] Fundamentos.
- [ ] Término de respuesta.
- [ ] Anexos (sección propia, aunque falten documentos: van entre corchetes).
- [ ] Última línea antes de las notificaciones: la advertencia de que, sin respuesta de fondo en el término legal, se acudirá a la acción de tutela.
- [ ] Notificaciones y firma.
- [ ] Dentro del escrito no hay instrucciones al abogado ni advertencias repetidas: el escrito le habla al destinatario.

## 8. Cierre

- [ ] Informe de verificación en `05-auditoria/`.
- [ ] Informe de riesgo en `05-auditoria/`.
- [ ] Decisión del Director en `06-decision/`.
- [ ] Constancia de radicación guardada en `01-entrada/pruebas/` cuando se presente: es la prueba de la fecha.
