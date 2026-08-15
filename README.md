# USTaxDeductionFinder.com

Sitio estático completo (HTML5 + CSS + JavaScript vanilla, sin build step) para
la calculadora de deducciones fiscales "Standard vs. Itemized" dirigida a
freelancers, conductores de Uber/Lyft, agentes inmobiliarios y creadores de
contenido en EE.UU. Incluye 20 artículos de blog SEO interlinkeados, páginas
legales, contacto y todo lo necesario para monetizar con Google AdSense.

## 🚀 Despliegue rápido (GitHub + Vercel)

1. **Crear el repositorio en GitHub**
   ```bash
   cd ustaxdeductionfinder
   git init
   git add .
   git commit -m "Initial launch: 20 articles + calculator"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/ustaxdeductionfinder.git
   git push -u origin main
   ```

2. **Importar en Vercel**
   - Entra a [vercel.com/new](https://vercel.com/new) y selecciona el repo.
   - Framework Preset: **Other** (sitio estático, no requiere build command).
   - Build Command: *(dejar vacío)* · Output Directory: `.` (raíz del repo).
   - Deploy. En 30–60 segundos tendrás una URL `https://tu-proyecto.vercel.app`.

3. **Migrar a tu dominio propio**
   - En el panel de Vercel: Project → Settings → Domains → agrega
     `ustaxdeductionfinder.com` y `www.ustaxdeductionfinder.com`.
   - Actualiza los registros DNS en tu proveedor de dominio (A/CNAME) según
     las instrucciones que Vercel muestra automáticamente.
   - Una vez propagado el DNS (unos minutos a 24 h), el sitio queda en vivo
     en tu dominio con HTTPS automático.

## 📁 Estructura del proyecto

```
ustaxdeductionfinder/
├── index.html                  → Home + calculadora "1040 Deduction Calculator"
├── contact.html                → Formulario de contacto
├── 404.html
├── sitemap.xml
├── robots.txt
├── vercel.json                 → Config de despliegue (cleanUrls, headers, cache)
├── css/styles.css              → Sistema de diseño completo
├── js/main.js                  → Menú, TTS, tamaño de fuente, compartir, progreso
├── js/calculator.js            → Motor de cálculo Standard vs. Itemized
├── images/                     → Favicon y og-cover (SVG, sin dependencias externas)
├── blog/
│   ├── index.html              → Índice del blog con sidebar de etiquetas
│   ├── tag-*.html               → 8 páginas de categoría/etiqueta
│   └── <slug>.html             → 20 artículos de lanzamiento
└── legal/
    ├── privacy-policy.html
    ├── terms-of-service.html
    └── disclaimer.html
```

## 💰 Antes de solicitar Google AdSense

1. Reemplaza el placeholder `ca-pub-XXXXXXXXXXXXXXXX` en cada `<head>`
   (buscar y reemplazar global en todos los `.html`, o regenerar con
   `python3 gen/gen.py` tras editar la constante en `gen/gen.py`).
2. Todos los bloques de anuncio están marcados con comentarios
   `<!-- ADSENSE AD REVENUE UNIT --> ` y `<!-- ADSENSE CONTENT AD HERE -->`
   dentro de `.ad-slot` — reemplázalos por el `<script>` de tu unidad de
   AdSense una vez aprobado.
3. Sube el sitio a tu dominio propio **antes** de aplicar a AdSense —
   Google exige un dominio propio, no un subdominio `.vercel.app`.
4. Envía la solicitud a mediados de noviembre para estar aprobado antes de
   la temporada alta de impuestos (enero–abril), tal como indica el plan
   financiero del proyecto.

## ✍️ Cómo agregar nuevos artículos (hasta 60 según el plan editorial)

Todo el contenido del blog se genera desde un único archivo Python, así que
nunca edites los `.html` de `/blog/` directamente — se sobrescriben.

1. Abre `gen/articles_data.py`.
2. Copia el bloque de un artículo existente dentro de la lista `ARTICLES` y
   edita: `slug`, `title`, `dek`, `meta_description`, `keywords`, `tags`,
   `publish_date` y `content` (HTML con `<h2>`, `<h3>`, `<ul>`, `<table>`,
   enlaces internos a otros artículos con `/blog/otro-slug.html`).
3. Ejecuta:
   ```bash
   cd gen && python3 gen.py
   ```
   Esto regenera automáticamente: la página del artículo, el índice del
   blog, las páginas de etiquetas, el sitemap.xml y los enlaces relacionados
   (related articles) según etiquetas compartidas.
4. Usa la solapa **"Plan de 60 Artículos"** del Excel de proyección
   (`04_Revenue_Projection_and_Content_Plan.xlsx`) como calendario editorial
   — ya trae keywords de cola larga, mes de publicación sugerido y estado.

## 🔧 Funcionalidades incluidas

- **Calculadora interactiva** de 4 pasos (perfil → ingresos/gastos →
  millaje → resultados), con spinner animado y motor de cálculo real
  (tope SALT $10,000, umbral médico 7.5% AGI) en `js/calculator.js`.
- **"Escuchar este artículo"** — usa la API gratuita y nativa del
  navegador `SpeechSynthesis` (Web Speech API). No requiere clave de API
  ni servicio de pago.
- **Aumentar/disminuir tamaño de letra**, persistente vía `localStorage`.
- **Botones de compartir**: X, Reddit, Facebook, WhatsApp, Email,
  Instagram (copia el link, ya que Instagram no permite compartir directo
  desde web) y "copiar enlace".
- **Tiempo de lectura estimado** calculado automáticamente por conteo de
  palabras en cada artículo.
- **Barra lateral de etiquetas/temas** para navegación directa por
  categoría, más buscador instantáneo en el índice del blog.
- **Interlinking real**: cada uno de los 20 artículos enlaza a 2–4 artículos
  relacionados dentro del cuerpo del texto, más un bloque de "Related
  Reading" al final calculado por etiquetas compartidas.
- **Schema.org / JSON-LD**: `WebApplication`, `FAQPage` y `Article` en
  cada página relevante para mejorar los resultados enriquecidos en Google.
- **Accesibilidad**: skip-link, foco visible, roles ARIA en controles.

## 📬 Activar el formulario de contacto

El formulario en `contact.html` es una demo estática (confirma en pantalla
pero no envía datos a ningún servidor). Para activarlo sin backend propio:

1. Crea una cuenta gratuita en [Formspree](https://formspree.io) (u otro
   servicio equivalente, como Web3Forms).
2. Reemplaza el `<form ...>` en `contact.html` para apuntar a tu endpoint:
   `<form action="https://formspree.io/f/TU_ID" method="POST">`
3. Elimina el `onsubmit="return handleContactSubmit(event)"` si prefieres
   el manejo nativo del servicio elegido.

## 📅 Mantenimiento anual obligatorio

Los siguientes valores están hardcodeados según el plan original (por
velocidad, sin llamadas a API) y **deben revisarse cada año fiscal**:

| Valor | Ubicación | Fuente oficial a verificar |
|---|---|---|
| Deducción estándar (Single/MFJ/HOH) | `js/calculator.js` → `STANDARD` | IRS.gov |
| Tope SALT ($10,000) | `js/calculator.js` → `SALT_CAP` | IRS.gov |
| Umbral médico (7.5% AGI) | `js/calculator.js` → `MEDICAL_AGI_THRESHOLD` | IRS.gov |
| Tarifa de millaje estándar | `js/calculator.js` → `mileageRate` | IRS.gov |

## 📄 Licencia

Código y contenido propiedad de Tax Tools Media Group para uso en
USTaxDeductionFinder.com. Ver `legal/terms-of-service.html`.
