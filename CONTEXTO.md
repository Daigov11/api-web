# Web Apiworking — contexto del proyecto

Versión en código del prototipo de Figma **"WEB APIWORKING"**: la Home y 11 páginas, una por rubro.
Fecha de este contexto: 2026-11-20.

## Reglas del proyecto (obligatorias)

1. **Una carpeta por módulo y un único `.html` por carpeta.** El HTML, el CSS (en `<style>`) y el JS (en `<script>`) van escritos dentro del mismo archivo.
   - **Motivo:** en Apiworking cada página se guarda en una base de datos como un bloque de código HTML. Un archivo equivale a una página completa.
2. **Ningún archivo usa otros archivos de este proyecto.** No se permite `src`, `href` ni `@import` hacia `../resto/...`, `estilos.css`, `app.js` ni nada parecido.
   - Las referencias web externas sí están permitidas: CDN, Google Fonts, URLs públicas.
   - La navegación entre páginas se hace con enlaces `<a href="/ruta">`.
3. **Imágenes:** pendiente de definir. Por ahora son marcadores CSS (`<div class="ph" role="img">`, sin `src`) con una etiqueta que dice qué foto va en cada lugar.

## Estructura

| Carpeta | Archivo | Ruta web | Página |
|---|---|---|---|
| inicio | index.html | `/` | Home |
| resto | resto.html | `/resto` | Restaurantes |
| fastfood | fastfood.html | `/fastfood` | Fast Food |
| tiendas | tiendas.html | `/tiendas` | Tiendas |
| hoteles | hoteles.html | `/hoteles` | Hoteles |
| ferreterias | ferreterias.html | `/ferreterias` | Ferreterías |
| minimarkets | minimarkets.html | `/minimarkets` | Minimarkets |
| talleres | talleres.html | `/talleres` | Talleres |
| asistencia | asistencia.html | `/asistencia` | Asistencia y Planillas |
| cocheras | cocheras.html | `/cocheras` | Cocheras |
| piscinas | piscinas.html | `/piscinas` | Piscinas |
| canchas | canchas.html | `/canchas` | Canchas |

- `_generador/`: herramienta de desarrollo. **No es una página** y no se sube a la base de datos.
- Las rutas web son provisionales y se pueden cambiar en `ROUTES` (`_generador/data.py`).
- La única referencia externa es Google Fonts (fuente Inter).
- Cada página es responsive: un mismo archivo sirve para escritorio y para móvil.

## Contenido de cada página de rubro

1. **Header:** el logo lleva a `/`. Tiene enlaces internos (`#como-funciona`, `#precios`, `#testimonios`) y el botón "Agendar demo", que abre un modal de consulta.
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
    - El formulario **no envía datos**: solo muestra un resumen, igual que el prototipo.

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
- [ ] Confirmar las URLs reales de cada página y actualizar `ROUTES`.
- [ ] Revisar los textos que se redactaron porque el Figma no se pudo capturar completo:
  - el subtítulo del hero de Restaurantes;
  - algunas estaciones;
  - las funciones de Restaurantes y la pestaña Administración de Fast Food;
  - varios beneficios;
  - las recompensas de algunas tarjetas Wallet;
  - las viñetas de los planes Básico, Completo y Hoteles;
  - los textos de los nodos.
- [ ] Conectar el formulario de consulta a un destino real.
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
- Una revisión con grep confirma que ningún archivo usa archivos locales del proyecto: los enlaces solo son `#`, `/ruta` o `https://`.
- Se probaron automáticamente con Playwright los modales, el panel de planes, los nodos, el visor, las pestañas y el formulario en los 11 rubros. No hubo errores de JS.
- En móvil (390 px) ninguna página se desborda a lo ancho.
