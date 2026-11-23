# Web Apiworking — contexto del proyecto

Las páginas son una **copia exacta** del prototipo de Figma **"WEB APIWORKING"**: la Home y 11 páginas, una por rubro, cada una con su versión de escritorio y su versión móvil.

- Figma: https://www.figma.com/proto/FOlwySZnBYyLc0rKWgWWI4/WEB-APIWORKING?node-id=10-14&starting-point-node-id=10%3A14
- Fecha de este contexto: 2026-11-23.

## Reglas del proyecto (obligatorias)

1. **Una carpeta por módulo y un único `.html` por carpeta.** El HTML, el CSS y el JS van dentro del mismo archivo.
   - **Motivo:** en Apiworking cada página se guarda como código HTML en una base de datos.
2. **Ningún archivo usa otros archivos del proyecto.** Solo se permiten referencias web externas:
   - Google Fonts;
   - imágenes en S3;
   - el endpoint del formulario.

   La navegación entre páginas usa URLs absolutas: `https://apiworking.com.pe/<ruta>/`.
3. **Se siguen las técnicas de `formulario.html`** (ver la sección "Técnicas de la guía").
4. **Copia exacta del Figma:** el diseño, los textos y el orden no se reinterpretan. Si algo cambia en el Figma, se regenera.
5. **Imágenes:** se alojan en el S3 de Apiworking y se suben con `POST https://api-centralizador.apiworking.pe/api/Data/images` (multipart, campo `image`, máximo 2 MB). La respuesta trae la `url`.

## Estructura

| Carpeta | Archivo | Ruta web | Frames de Figma (escritorio / móvil) |
|---|---|---|---|
| inicio | index.html | `/` | 10:2 / 54:2464 |
| resto | resto.html | `/sistema-para-restaurantes/` | 10:14 / 10:26 |
| fastfood | fastfood.html | `/fastfood/` (provisional) | 10:38 / 10:50 |
| tiendas | tiendas.html | `/sistema-gestion-y-facturacion-electronica-para-tienda-pymes/` | 10:62 / 10:74 |
| hoteles | hoteles.html | `/sistema-de-gestion-para-hoteles/` | 10:86 / 10:98 |
| ferreterias | ferreterias.html | `/sistema-gestion-y-facturacion-electronica-para-ferreterias/` | 10:110 / 10:122 |
| minimarkets | minimarkets.html | `/sistema-de-gestion-y-facturacion-para-minimarket/` | 10:134 / 10:146 |
| talleres | talleres.html | `/sistema-de-gestion-para-talleres-mecanicos/` | 10:158 / 10:170 |
| asistencia | asistencia.html | `/asistencia/` (provisional) | 10:182 / 10:194 |
| cocheras | cocheras.html | `/sistema-cocheras/` | 10:206 / 10:218 |
| piscinas | piscinas.html | `/piscinas/` (provisional) | 10:230 / 10:242 |
| canchas | canchas.html | `/sistema-canchas-deportivas/` | 10:254 / 10:266 |

- Las rutas y el dominio se definen en `ROUTES` y `BASE_URL` (`_generador/data.py`).
- Cada página pesa entre 0,6 y 0,9 MB. Incluye:
  - la versión de escritorio y la versión móvil;
  - todas sus capas superpuestas (demo, consulta preparada, detalle de nodos, modal de función, planes ampliados, vistas NFC);
  - las variantes del explorador y de la planta.

## Cómo se generan (convertidor Figma → HTML)

Las páginas **no se editan a mano**: se generan desde el Figma con `_generador/figma/`.

```bash
python3 _generador/figma/build_all.py            # las 12 páginas
python3 _generador/figma/build_all.py resto      # solo una (claves: inicio, resto, fastfood, ...)
```

| Archivo | Qué hace |
|---|---|
| `figapi.py` | Acceso a la API de Figma y a la de imágenes de Apiworking. Lleva la caché y optimiza imágenes con `sips` (JPG/PNG por debajo de 2 MB). |
| `fig2html.py` | Convierte nodos a HTML con estilos en línea. El diseño automático de Figma se traduce a flexbox; el resto de nodos se posicionan de forma absoluta. Copia rellenos, bordes, sombras, radios y texto con estilos mixtos. |
| `svgrender.py` | Dibuja como SVG vectores, íconos, ilustraciones y texto en curva a partir de su geometría exacta. Sustituye al renderizado de Figma, que tiene cupo. |
| `build_fig.py` | Resuelve los recursos: sube las imágenes a S3 y genera o inserta los SVG. |
| `pagina.py` | Traduce las interacciones del prototipo y convierte los campos del formulario en inputs reales. Corrige los textos que decían que el formulario no envía datos. |
| `shell.py` | Envoltorio de la página con las técnicas de la guía, más el motor de interacciones y el formulario. |
| `assets.json` | Mapa de recursos → URL en S3. Se versiona para no volver a subir lo mismo. |
| `cache/` | Copia local del archivo de Figma completo, de unos 186 MB. **No va a git.** |

**Token de Figma:** está en `~/.figma_token` y es de solo lectura. Nunca va al repositorio.

**Cupo de la API de Figma:** la cuenta es de solo lectura y tiene un cupo muy bajo.
- El renderizado de imágenes (`/v1/images`) quedó bloqueado unos 4,6 días a partir del 2026-11-23. Por eso existe `svgrender.py`.
- Para regenerar no hace falta la API, porque se usa la copia en `cache/full_file.json`.
- Si el Figma cambia, hay que volver a descargar el archivo completo con **una sola** petición:
  ```bash
  curl -H "X-Figma-Token: $(cat ~/.figma_token)" \
    "https://api.figma.com/v1/files/FOlwySZnBYyLc0rKWgWWI4?geometry=paths" \
    -o _generador/figma/cache/full_file.json
  ```
  Después hay que volver a crear los `node_*.json` y el `index.json` del mismo directorio.

`_generador/legacy_build.py` es el generador anterior (hecho a mano, no exacto). **Ya no se usa.** Ejecutarlo sobrescribiría las páginas.

## Técnicas de la guía `formulario.html`

1. **Capa propia:** todo va dentro de `<div class="awx-overlay awx-landing">`, una capa fija a pantalla completa con su propio scroll que tapa el contenedor del CMS.
2. **Estilos en línea en cada elemento**, más un reinicio con prefijo `.awx-landing`. Así los estilos del CMS no los alteran.
3. **Sin clearfix ni pseudo-elementos del CMS:** se anulan en los `div`.
4. **JS en ES5, encapsulado:** sin variables globales y con el `<script>` dentro de la capa.
5. **Sin entidades HTML.**
6. **Anclas por JS** (`scrollIntoView`), sin cambiar la URL del CMS.

## Escalado y móvil

- El diseño de escritorio mide 1440 px de ancho y el móvil 390 px. El JS aplica `zoom = ancho / 1440` o `ancho / 390`, así que la página se ve proporcionalmente igual al Figma en cualquier pantalla.
- Hasta 700 px de ancho se muestra el frame móvil; desde ahí, el de escritorio.
- Las capas superpuestas se escalan con la misma regla.

## Interacciones (motor en `shell.py`)

| Interacción del prototipo | Comportamiento en la página |
|---|---|
| Navegar a otro frame | Enlace a la ruta de esa página. |
| Desplazarse a | Desplazamiento suave a la sección. |
| URL | Abre el enlace en una pestaña nueva (por ejemplo, el video de YouTube). |
| Capa superpuesta / cambiar capa / cerrar / atrás | Capas con fondo oscurecido. Se cierran con Escape o con clic fuera. |
| Cambiar a (variantes) | Cambia la instancia por la variante, con entrada escalonada. |
| Rueda de 25 variantes y espigas | Animación CSS continua. En la rueda y en las enredaderas del ecosistema, el anillo exterior gira en sentido horario y el interior al revés. |
| Botones "Sin movimiento" / "Activar movimiento" y etiquetas "VISTA SIN MOVIMIENTO" | **Ocultos** (pedido del usuario, 2026-11-23). Las animaciones siempre corren; solo se detienen si el sistema tiene activada la opción de reducir movimiento. |
| Tarjetas del explorador | Entran escalonadas al aparecer la sección y al cambiar de pestaña, y se elevan al pasar el mouse. |
| "Ver giro", "Ver crecer", "Ver entrada escalonada" | **Automáticos** (pedido del usuario, 2026-11-23). La rueda gira siempre, la planta crece en bucle (Semilla → Brote → Creciendo → Plena) y el explorador hace su entrada al aparecer en pantalla. Los botones se ocultan, pero conservan su espacio. |
| "Sin movimiento" / "Cambiar movimiento" | Activa o desactiva todas las animaciones. |
| Variables de Figma | La API no da sus valores. El modal de función muestra la función pulsada y el rubro. |
| Hover del explorador | No se replica: depende de variables que la API no expone. |

## Formulario de contacto

- **Dónde está:** en la sección "Prepara tu consulta" de cada rubro y en la capa "Demo emergente".
- **Campos:** los frames "Entrada · X" se convierten en inputs reales con el mismo estilo.
- **Envío:** "Preparar mi consulta" hace un `POST` a `https://api-centralizador.apiworking.pe/api/Administrativo/sendFormContact` con estos datos:
  - `nombreCompleto`
  - `telefono`: solo dígitos.
  - `nombreNegocio`
  - `giroNegocio`: el rubro, seguido de los datos extra separados por `|`.
  - `ipCreacion`: obtenida de ipify.
  - `destinatarios`: los mismos de `formulario.html`.
- **Después de enviar:** se ejecuta la acción del prototipo. En la demo pasa a "Consulta preparada"; en la página baja a la revisión.
- **Textos corregidos:** los del diseño que decían "no guarda ni envía datos" se cambiaron por textos correctos (`TEXT_FIX` en `pagina.py`).

## Pendientes

- [ ] En pausa (2026-11-23), por decisión del usuario: Fast Food, Asistencia y Piscinas aún no tienen contenido en el sitio, así que se dejan con sus rutas provisionales hasta nuevo aviso.
- [x] Envío real de prueba desde el CMS: el usuario lo probó el 2026-11-23 y el correo llegó.
- [ ] Revisión visual página por página contra el Figma. Restaurantes escritorio se comparó píxel a píxel; el resto se revisó por muestreo.
- Anillo exterior de la rueda (pedido del usuario, 2026-11-23):
  - cada palabra aparece una sola vez y se añaden **"Logística"** y **"Luka IA"**;
  - el texto se ajusta para cubrir todo el círculo (`textLength`);
  - el anillo interior repite sus palabras hasta llenarlo.
- [ ] Peso de las páginas, de 0,6 a 0,9 MB. Se puede reducir si la base de datos tiene límite.

## Verificación realizada (2026-11-23)

- Restaurantes escritorio: misma altura que el Figma (14 539 px) y comparación sección por sección prácticamente idéntica.
- Las 12 páginas:
  - 0 imágenes rotas y 0 errores de JS;
  - todas las capas de escritorio abren;
  - el formulario envía el JSON esperado (endpoint simulado);
  - el móvil se ve sin desbordes.
- Las referencias son solo Google Fonts, S3 y las APIs; ningún archivo usa otro del proyecto.
