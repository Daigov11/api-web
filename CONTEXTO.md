# Web Apiworking — contexto del proyecto

Versión en código del prototipo de Figma **"WEB APIWORKING"**: la Home y 11 páginas, una por rubro.
Fecha de este contexto: 2026-11-21.

## Reglas del proyecto (obligatorias)

1. **Una carpeta por módulo y un único `.html` por carpeta.** El HTML, el CSS (en `<style>`) y el JS (en `<script>`) van escritos dentro del mismo archivo.
   - **Motivo:** en Apiworking cada página se guarda en una base de datos como un bloque de código HTML. Un archivo equivale a una página completa.
2. **Ningún archivo usa otros archivos de este proyecto.** No se permite `src`, `href` ni `@import` hacia `../resto/...`, `estilos.css`, `app.js` ni nada parecido.
   - Las referencias web externas sí están permitidas: CDN, Google Fonts, URLs públicas.
   - La navegación entre páginas se hace con enlaces absolutos `<a href="https://apiworking.com.pe/ruta/">`, igual que en `formulario.html`.
3. **Seguir las técnicas de `formulario.html`** (la guía de cómo se arman las páginas para el CMS de Apiworking). Ver la sección siguiente.
4. **Imágenes:** pendiente de definir. Por ahora son marcadores CSS (`<div class="ph" role="img">`, sin `src`) con una etiqueta que dice qué foto va en cada lugar.

## Técnicas de la guía `formulario.html`

`formulario.html` (en la raíz) es la referencia de cómo se armaban las páginas para que sus estilos se impongan sobre el contenedor HTML del CMS. No es un módulo. Todas las páginas aplican sus técnicas:

1. **Capa propia:** todo el contenido va dentro de `<div class="awx-overlay awx-landing">`. Es una capa fija a pantalla completa (`position:fixed; inset:0; z-index:9999`) que tapa el contenedor del CMS y tiene su propio scroll.
2. **CSS con prefijo:** cada regla empieza por `.awx-landing`, para ganarle a los estilos del CMS sin afectarlos. El generador añade el prefijo solo (`scope_css`); en `build.py` el CSS se escribe sin prefijo.
   - `:root` y `body` pasan a `.awx-landing`; `html` pasa a `.awx-overlay`.
3. **Sin clearfix del CMS:** se anulan los `::before`/`::after` que el CMS pone a contenedores como `.wrap`.
4. **Sin choques con Bootstrap:** las clases `.modal` y `.lead` se renombran como `.awx-modal` y `.awx-lead`.
5. **JS encapsulado y en ES5** (`var`, `function`): todo dentro de una función, sin variables globales en `window`, y las búsquedas limitadas a la capa `.awx-landing`. El `<script>` va dentro de la capa, al final.
6. **Anclas por JS:** los enlaces `#seccion` se resuelven con `scrollIntoView` dentro de la capa, sin cambiar la URL del CMS.
7. **Sin entidades HTML** (`&nbsp;`, `&amp;`…): se usan los caracteres directos.

## Formulario de contacto (endpoint)

Los formularios de consulta envían los datos al endpoint de Apiworking, igual que `formulario.html`.

- **Endpoint:** `POST https://api-centralizador.apiworking.pe/api/Administrativo/sendFormContact` (JSON). Acepta CORS desde cualquier origen.
- **Cuerpo:** `nombreCompleto`, `telefono` (solo dígitos, mínimo 7), `nombreNegocio`, `giroNegocio`, `ipCreacion` (obtenida de api.ipify.org) y `destinatarios`.
- **`giroNegocio`:** el endpoint no tiene campos para plan, locales, especialidad ni necesidad. Por eso se envía el rubro en mayúsculas y, después, esos datos separados por `|`. Ejemplo: `RESTAURANTES | Locales: 1 local | Plan: STANDARD · S/ 949 al año`.
- **Destinatarios:** son los mismos correos de `formulario.html` y se definen en `FORM_DEST` (`_generador/build.py`).
- **Dónde está:** en cada página de rubro, en el modal "Agendar demo / Elegir plan" y en la sección "Prepara tu consulta". La Home no tiene formulario.
- **Comportamiento:**
  - valida los datos y muestra avisos si falta algo;
  - mientras envía, el botón dice "Enviando..." y muestra un indicador de carga;
  - si el envío funciona, limpia el formulario y abre la confirmación "Recibimos tu consulta.";
  - si falla, muestra "Error al enviar. Intenta nuevamente.".

## Estructura

| Carpeta | Archivo | Ruta web | Página |
|---|---|---|---|
| inicio | index.html | `/` | Home |
| resto | resto.html | `/sistema-para-restaurantes` | Restaurantes |
| fastfood | fastfood.html | `/fastfood` (provisional) | Fast Food |
| tiendas | tiendas.html | `/sistema-gestion-y-facturacion-electronica-para-tienda-pymes` | Tiendas |
| hoteles | hoteles.html | `/sistema-de-gestion-para-hoteles` | Hoteles |
| ferreterias | ferreterias.html | `/sistema-gestion-y-facturacion-electronica-para-ferreterias` | Ferreterías |
| minimarkets | minimarkets.html | `/sistema-de-gestion-y-facturacion-para-minimarket` | Minimarkets |
| talleres | talleres.html | `/sistema-de-gestion-para-talleres-mecanicos` | Talleres |
| asistencia | asistencia.html | `/asistencia` (provisional) | Asistencia y Planillas |
| cocheras | cocheras.html | `/sistema-cocheras` | Cocheras |
| piscinas | piscinas.html | `/piscinas` (provisional) | Piscinas |
| canchas | canchas.html | `/sistema-canchas-deportivas` | Canchas |

- `_generador/`: herramienta de desarrollo. **No es una página** y no se sube a la base de datos.
- Las rutas son las URLs reales de apiworking; por ejemplo, la página original de Restaurantes es `/sistema-para-restaurantes`. Se definen en `ROUTES` y el dominio en `BASE_URL` (`_generador/data.py`). Los enlaces salen como `https://apiworking.com.pe/<ruta>/`. Fast Food, Asistencia y Piscinas aún no tienen ruta real.
- Referencias externas: Google Fonts (Inter), el endpoint del formulario y api.ipify.org.
- Cada página es responsive: un mismo archivo sirve para escritorio y para móvil.

## Contenido de cada página de rubro

1. **Header:** el logo lleva a la Home. Tiene enlaces internos (`#como-funciona`, `#precios`, `#testimonios`) y el botón "Agendar demo", que abre un modal de consulta.
2. **Hero:** rueda con el botón "Ver giro" y una tarjeta de estado. Rappi y PedidosYa aparecen solo en resto y fastfood.
3. **Franja de valor.**
4. **Ecosistema:** 6 nodos y cada uno abre un panel con su propio texto. Incluye la planta "Ver crecer" y el botón "Sin movimiento".
5. **Pack:** 3 piezas con visor "Ampliar", tarjeta Wallet, Push/GeoPush, el bloque "Así se conecta" y una nota "POR VALIDAR".
6. **Secciones especiales según el rubro:**
   - Ojo de Águila: resto y hoteles
   - Balanza: minimarkets
   - ApiReview: talleres
   - ZKTeco: asistencia
7. **Así funciona** (`#como-funciona`): estaciones y 5 etapas.
8. **Funciones:** 6 pestañas con 4 tarjetas cada una (24 en total). Cada tarjeta abre un modal de detalle con el aviso "Video demostrativo pendiente de enlace".
9. **Beneficios, Yape y Qubit.** Asistencia no los muestra (bandera `no_payments`).
10. **Precios:** 4 planes (Asistencia tiene solo APISTAFF).
    - "Elegir" abre la consulta con el plan ya cargado.
    - "VER MÁS +" abre un panel lateral que se cierra con la ×, con Escape o haciendo clic fuera.
11. **Testimonios:** por ahora es un marcador.
12. **FAQ, formulario de consulta y footer.**
    - El FAQ tiene 5 preguntas.
    - El formulario envía los datos al endpoint de Apiworking (ver la sección del formulario).

La Home (`inicio/index.html`) contiene, en este orden:
- el hero con su collage y la tarjeta ApiLoyalty;
- las cifras 11 / 264;
- "Cómo funciona";
- la cuadrícula de los 11 rubros;
- ApiLoyalty + NFC;
- el FAQ, el CTA final y el footer.

## Correcciones respecto al Figma

- El panel "Ver más" de los planes ahora tiene botón de cierre.
- Cada nodo del ecosistema muestra su propio texto.
- "Cómo funciona" lleva a la sección Así funciona.
- Erratas corregidas:
  - "MÚILTIPLES" → "múltiples"
  - "solicitar sistema…" → "Solicitar sistema…", con mayúscula inicial
- En los rubros que no son de comida ya no aparece "Comandas y precuentas".
- La estación 02 de Piscinas ya no repite el texto de Cocheras.
- Asistencia ya no muestra Yape ni Qubit.
- El visor "Ampliar" ahora cabe en pantallas bajas.

## Pendientes

- [ ] Definir cómo se manejarán las imágenes y reemplazar los marcadores `.ph`. Las mascotas son emojis provisionales.
- [ ] Definir la ruta real de Fast Food, Asistencia (¿`/ecosistema/apistaff`?) y Piscinas.
- [ ] Revisar los textos que se redactaron porque el Figma no se pudo capturar completo:
  - el subtítulo del hero de Restaurantes;
  - algunas estaciones;
  - las funciones de Restaurantes y la pestaña Administración de Fast Food;
  - varios beneficios;
  - las recompensas de algunas tarjetas Wallet;
  - las viñetas de los planes Básico, Completo y Hoteles;
  - los textos de los nodos.
- [ ] Hacer un envío real de prueba desde el CMS. En local se probó con el endpoint simulado.
- [ ] Decidir si se usa el logo real que aparece en `formulario.html`. Ahora el logo es texto.
- [ ] Añadir los enlaces de los videos demostrativos y los testimonios reales.

## Cómo regenerar las páginas

Las 12 páginas se generan con un script en Python a partir de una plantilla común y de los datos de cada rubro.

```bash
python3 _generador/build.py .
```

- `_generador/data.py` contiene los textos, planes, rutas y banderas de cada rubro.
- `_generador/build.py` contiene la plantilla, el CSS y el JS compartidos, y escribe las 12 páginas.
- **Atención:** regenerar **sobrescribe** los HTML. Si editaste un HTML a mano, pasa ese cambio al generador antes de volver a ejecutarlo, o lo perderás.

## Verificación realizada

- `node --check` pasa en el JS de las 12 páginas.
- Una revisión con grep confirma que ningún archivo usa archivos locales del proyecto: los enlaces solo son `#` o `https://`.
- Se probaron automáticamente con Playwright los modales, el panel de planes, los nodos, el visor, las pestañas y las anclas en los 11 rubros, con Bootstrap 3 cargado encima para simular el CMS. No hubo errores de JS.
- También se probaron, con el endpoint simulado, la validación, el envío correcto (revisando el JSON enviado), el envío con plan elegido y el error del servidor.
- En móvil (390 px) ninguna página se desborda a lo ancho dentro de la capa.
