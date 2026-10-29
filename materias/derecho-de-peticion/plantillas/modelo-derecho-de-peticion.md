# Plantilla de Derecho de Petición — Despacho Pessoa

> **Instrucciones para el Redactor (*Ricardo Reis*):**
> 1. Usa estrictamente esta estructura y este orden: hechos, peticiones, fundamentos, término.
> 2. Cada hecho de la sección **HECHOS** termina con la etiqueta `[Fuente: HECHO-XX de hechos.md — Prueba P-YY]`.
> 3. Cada norma o sentencia de la sección **FUNDAMENTOS** reproduce la cita textual entre comillas y termina con `[Fuente: FICHA-XX de investigacion.md — Archivo: fuentes/...]`.
> 4. Si un dato fue marcado `NO CONSTA` por el Observador, deja el marcador `[NO CONSTA EN EL EXPEDIENTE — COMPLETAR POR EL SOCIO DIRECTOR]`. No lo inventes.
> 5. Elige una sola persona gramatical (primera si el peticionario actúa en causa propia; tercera si actúa apoderado o agente oficioso) y sostenla de principio a fin.
> 6. El escrito le habla al destinatario. Las advertencias para el abogado van en tu Reporte de Cierre, no aquí.

---

```markdown
Señor(a)
**[CARGO Y NOMBRE DE LA DEPENDENCIA DEL DESTINATARIO, según hechos.md]**
**[NOMBRE DE LA ENTIDAD O DEL PARTICULAR]**
[Ciudad según hechos.md o marcador [NO CONSTA EN EL EXPEDIENTE — COMPLETAR POR EL SOCIO DIRECTOR]]

**Referencia:** Derecho de petición (artículo 23 de la Constitución Política y Ley 1755 de 2015) en la modalidad de [información / copia de documentos / consulta / queja / reclamo / petición en interés particular].
**Peticionario(a):** [Nombre completo según hechos.md]
**Identificación:** [Cédula según hechos.md o marcador]

Yo, **[NOMBRE DEL PETICIONARIO O DE SU APODERADO]**, mayor de edad, identificado(a) con cédula de ciudadanía No. **[NÚMERO SEGÚN HECHOS.MD]**, actuando en **[nombre propio / calidad de apoderado(a) de NOMBRE DEL TITULAR, según poder adjunto]**, presento ante ustedes **DERECHO DE PETICIÓN** con fundamento en los siguientes

## I. HECHOS
*(Solo hechos catalogados como PROBADOS en `hechos.md`. Breves, numerados y en orden cronológico; únicamente los necesarios para que el destinatario entienda qué se pide y por qué le corresponde).*

1. **[Primer hecho]** `[Fuente: HECHO-01 de hechos.md — Prueba P-YY]`.
2. **[Segundo hecho]** `[Fuente: HECHO-02 de hechos.md — Prueba P-YY]`.
3. **[Continuar según hechos.md...]**

## II. PETICIONES
*(Numeradas, una por punto, de modo que cada una pueda responderse por separado. Solo las que `investigacion.md` marcó como viables).*

**PRIMERA:** [Petición concreta y determinada].
**SEGUNDA:** [Petición concreta y determinada].
**TERCERA:** [Si aplica: copia de documentos o información puntual, identificada].

## III. FUNDAMENTOS DE DERECHO
*(Citar exclusivamente las normas y sentencias autorizadas en `investigacion.md`, con el extracto textual entre comillas y el archivo de origen).*

1. **Derecho fundamental de petición.**
   > "[Cita textual del artículo 23 de la Constitución Política]" `[Fuente: FICHA-XX de investigacion.md — Archivo: fuentes/00_transversal/constitucion_art_23_86.md]`.

2. **Objeto, modalidad y término de la petición.**
   > "[Cita textual del artículo 13 o del artículo 14 de la Ley 1755 de 2015, según la modalidad]" `[Fuente: FICHA-XX de investigacion.md — Archivo: fuentes/00_transversal/ley_1755_de_2015_peticion.md]`.

3. **[Si el destinatario es un particular] Petición ante organizaciones privadas.**
   > "[Cita textual del artículo 32 de la Ley 1755 de 2015]" `[Fuente: FICHA-XX de investigacion.md — Archivo: fuentes/00_transversal/ley_1755_de_2015_peticion.md]`.

4. **Qué cuenta como respuesta de fondo.**
   > "[Cita textual de la jurisprudencia autorizada sobre respuesta clara, precisa, congruente y consecuente]" `[Fuente: FICHA-XX de investigacion.md — Archivo: fuentes/00_transversal/corte_const_derecho_de_peticion_respuesta_de_fondo_T-329_2021_T-197_2024.md]`.

5. **[Otras normas o sentencias con ficha, según la materia del caso: salud, laboral, habeas data]**

## IV. TÉRMINO DE RESPUESTA
*(Un párrafo por cada término que aplique. El vencimiento sale de `herramientas/calcular_plazos.py`, transcrito desde `hechos.md`; nunca se cuenta aquí).*

De conformidad con el artículo 14 de la Ley 1755 de 2015, esta petición debe resolverse dentro de los **[quince (15) / diez (10) / treinta (30)] días** siguientes a su recepción. `[Fuente: FICHA-XX de investigacion.md — Archivo: fuentes/00_transversal/ley_1755_de_2015_peticion.md]`

[Solo en la modalidad de documentos e información: advertir lo que dispone el numeral 1 del artículo 14 sobre el silencio, con su cita textual y su ficha.]

## V. ANEXOS
*(Sección propia siempre. Lo que falte va entre corchetes, no se omite).*

1. [Copia de documento probado — `Prueba P-01`]
2. [Copia de documento probado — `Prueba P-02`]
3. [Poder, si actúa apoderado — `Prueba P-XX` o marcador]

De no obtener respuesta de fondo, clara y completa dentro del término legal, acudiré a la acción de tutela por violación del derecho fundamental de petición.

## VI. NOTIFICACIONES
Recibiré notificaciones en [dirección física, correo electrónico y teléfono según `hechos.md`, o marcador `[NO CONSTA EN EL EXPEDIENTE — COMPLETAR POR EL SOCIO DIRECTOR]`].

Atentamente,

__________________________________________
**[NOMBRE DEL PETICIONARIO O APODERADO]**
C.C. No. [NÚMERO SEGÚN HECHOS.MD]
[T.P. No. ____ del C.S. de la J., si actúa abogado]
```

---

BORRADOR PARA REVISIÓN HUMANA — No apto para radicar sin informe de verificación, informe de riesgo y firma del Socio Director.
