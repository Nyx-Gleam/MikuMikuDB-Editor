# MikuMikuDB Editor

🌐 **Idioma:** [English](./README.md) | Español | [日本語](./README_JA.md)

[![Latest Release](https://img.shields.io/github/v/release/Nyx-Gleam/MikuMikuDB-Editor?include_prereleases)](https://github.com/Nyx-Gleam/MikuMikuDB-Editor/releases)
[![License: MIT](https://img.shields.io/github/license/Nyx-Gleam/MikuMikuDB-Editor)](./LICENSE)
[![Downloads](https://img.shields.io/github/downloads/Nyx-Gleam/MikuMikuDB-Editor/total)](https://github.com/Nyx-Gleam/MikuMikuDB-Editor/releases)
[![Issues](https://img.shields.io/github/issues/Nyx-Gleam/MikuMikuDB-Editor)](https://github.com/Nyx-Gleam/MikuMikuDB-Editor/issues)

> Aplicación GUI para generar archivos `mod_pv_db.txt` para packs de canciones personalizados de Project Diva.
>
> **Versión 2.0 BETA** — reconstruida desde cero sobre PySide6 (Qt), con un código modular, un único build trilingüe (inglés/español/japonés) y un gran número de herramientas nuevas y correcciones respecto a la versión original en Tkinter.
 
---
 
## Índice
 
1. [Descripción general](#descripción-general)
2. [Novedades de la 2.0](#novedades-de-la-20)
3. [Funciones principales](#funciones-principales)
4. [Requisitos técnicos](#requisitos-técnicos)
5. [Instalación](#instalación)
6. [Uso paso a paso](#uso-paso-a-paso)
7. [Configuración y autoguardado](#configuración-y-autoguardado)
8. [Exportar `mod_pv_db.txt`](#exportar-mod_pv_dbtxt)
9. [Estructura del proyecto](#estructura-del-proyecto)
10. [Licencia](#licencia)
11. [Agradecimientos](#agradecimientos)
---
 
## Descripción general
 
MikuMikuDB Editor simplifica la creación de `mod_pv_db.txt`, el archivo de configuración que impulsa los packs de canciones personalizados en Project Diva. Con una interfaz intuitiva, permite definir metadatos del pack, datos de cada canción, niveles de dificultad, créditos, letras, efectos de sonido, intérpretes y varias variantes de audio por tema, todo sin escribir código.
 
* **Interfaz:** inglés, español y japonés, intercambiables en cualquier momento desde Ajustes (ya no hay builds separados por idioma).
* **Distribución:** un único ejecutable para Windows 10/11, sin necesidad de Python ni dependencias.
* **Salida:** guardados de proyecto `.pdpack` cifrados, más un `mod_pv_db.txt` final en UTF-8.
---
 
## Novedades de la 2.0
 
Esta versión es una reescritura completa de la aplicación, no solo una actualización de funciones:
 
* **Nuevo framework de interfaz:** migración de Tkinter a **PySide6 (Qt)** — tema oscuro nativo, arrastrar y soltar nativo, y escalado HiDPI que ya no necesita un sistema de escalado manual.
* **Vista previa de audio instantánea:** el motor anterior exportaba cada vista previa a un WAV temporal y lo reproducía mediante un subproceso; el nuevo usa `QMediaPlayer` directamente, así que la reproducción y el avance son instantáneos y sin archivos temporales.
* **Interfaz realmente trilingüe:** inglés, español y japonés conviven ahora en un solo build y se pueden cambiar desde Ajustes en cualquier momento.
* **Dos pestañas nuevas en el editor de canciones:**
  * **Letras** — importación desde `.txt`, `.srt`, `.vtt`, `.ass`, `.ssa` o `.lrc`, con sincronización de líneas entre japonés e inglés.
  * **SFX** — configuración de efectos de sonido Button, Slide, Chain Slide, Slider Touch y Chance por canción.
* **Calculadora de BPM** — tap-tempo (con rechazo de valores atípicos y promediado) más detección automática opcional a partir del archivo de audio.
* **Nuevo campo en Song Info:** Ilustrador.
* **Nuevo campo opcional:** lectura del nombre de la canción en inglés (Song Name Reading EN).
* **Explorador de mods instalados** — escanea tu carpeta de mods, permite buscar canciones por nombre/ID/artista en todos ellos, e importar o exportar canciones entre un mod instalado y tu proyecto actual. Las canciones vanilla se excluyen del conteo para que los totales sean correctos.
* **Validador de archivos multimedia** — comprueba que los archivos de audio, video y variantes de cada canción realmente existan en el disco.
* **Crear carpetas faltantes** — genera `sound/song`, `movie`, `script` y `2d`, además de un `config.toml` por defecto si falta.
* **Validación de PV ID en línea** — verifica si un PV ID ya está usado o reservado antes de que lo confirmes.
* Se incluye ahora, por separado, una herramienta independiente de diagnóstico: el **Decryptor Tool de `.pdpack`**.
* La reescritura sacó a la luz una larga lista de correcciones, entre ellas: un formato de cifrado que nunca podía volver a abrirse, colisiones de nombre de archivo en los autoguardados, un cuelgue grave al iniciar, una ruta de carpeta de mods escrita a mano, y rangos de nivel de dificultad incorrectos.
---
 
## Funciones principales
 
1. **Metadatos del pack**
   * Ingresa el **Pack Name** (en caracteres romanos) y, opcionalmente, el **nombre en japonés**.
2. **Biblioteca de canciones**
   * Administra varias canciones en una tabla: **PV ID**, **nombre original**, **nombre en inglés**.
   * Agrega, edita o elimina canciones con botones dedicados.
3. **Editor de canciones** (diálogo de 7 pestañas)
   * **Información básica:** PV ID, títulos original e inglés, lectura en hiragana, título romanizado, BPM (con calculadora de tap/auto-detección), fecha (AAAAMMDD), inicio y duración del estribillo (Sabi).
   * **Dificultades:** habilita Easy/Normal/Hard/Extreme/Extra Extreme; asigna a cada una un código `PV_LV_XX_X` válido dentro del rango correcto para esa dificultad.
   * **Intérpretes:** elige hasta seis vocaloids entre Hatsune Miku, Kagamine Rin/Len, Megurine Luka, KAITO, MEIKO, Yowane Haku, Akita Neru, Sakine Meiko y Kasane Teto.
   * **Song Info:** campos opcionales para arreglista, letrista, compositor/artista, manipulador, guitarrista, ilustrador y editor de PV — cada uno en original e inglés.
   * **Letras:** escribe o importa letras en japonés/inglés, con importación desde formatos de subtítulos y sincronización de líneas.
   * **Variantes de audio:** define mezclas alternativas o dúos con su propio nombre, artista, sufijo y lista de intérpretes; se exige lectura en hiragana donde corresponde.
   * **SFX:** configura los efectos de sonido Button, Slide, Chain Slide, Slider Touch y Chance.
4. **Autoguardado y guardado manual**
   * Copias de seguridad automáticas en `.pdpack` cada 5 minutos (hasta 60 archivos).
   * **Save Configuration** / **Load Configuration** manuales para archivos de proyecto cifrados, con migración automática de formatos antiguos.
5. **Mods y PV IDs**
   * Explora los mods instalados y sus canciones, busca en todos ellos y mueve canciones entre un mod y tu proyecto actual.
   * Valida PV IDs contra la base de datos en línea de IDs usados/reservados.
6. **Exportación final**
   * Haz clic en **Generate File** para crear un `mod_pv_db.txt` en UTF-8 listo para un pack de Project Diva.
   * Vuelve a importar ese mismo archivo cuando quieras con **Import mod_pv_db.txt** para seguir editándolo.
---
 
## Requisitos técnicos
 
* **Windows 10 u 11** (se recomienda 64-bit).
* **Build independiente:** no requiere instalar Python ni librerías; solo ejecutar el `.exe`.
* **Ejecutando desde el código fuente:** Python 3.12+, además de `PySide6`, `cryptography` y `requests`. Opcionales: `pykakasi` (generación automática de hiragana) y `toml` (lectura de `config.toml`), ambos instalables vía `pip`. La detección automática de BPM además necesita `numpy` (vía `pip`) y **`madmom`, que *no* se instala con `pip install madmom`** — hay que obtenerlo directamente desde su [repositorio de GitHub](https://github.com/CPJKU/madmom) y seguir sus propias instrucciones de instalación.
---
 
## Instalación
 
### Instalación rápida (GitHub)
 
1. Visita la página de [GitHub Releases](https://github.com/Nyx-Gleam/MikuMikuDB-Editor/releases).
2. Descarga la última versión de `MikuMikuDB Editor.exe`.
3. Haz doble clic para ejecutarlo; si Windows advierte sobre un editor desconocido, clic derecho → **Propiedades** → marca **Desbloquear** → **Aplicar**, y vuelve a ejecutarlo.
### Instalación alternativa (GameBanana)
 
1. Ve a la [página de GameBanana](https://gamebanana.com/tools/19907) de esta herramienta.
2. Descarga la última versión del editor.
3. Haz doble clic en `Editor.exe` para iniciarlo — no requiere instalación.
   * Si Windows muestra una advertencia de seguridad: clic derecho en el archivo → **Propiedades** → marca **Desbloquear** al final → **Aplicar** → **Aceptar**.
### Ejecutar desde el código fuente
 
1. Clona el repositorio:
```bash
   git clone https://github.com/Nyx-Gleam/MikuMikuDB-Editor.git
   cd MikuMikuDB-Editor
```
2. Crea un entorno virtual (usa el comando que funcione en tu sistema — `py` o `python`):
```bash
   py -m venv venv
   # o
   python -m venv venv
```
3. Actívalo:
```bash
   .\venv\Scripts\activate
```
4. Instala las dependencias:
```bash
   pip install -r requirements.txt
```
5. Ejecuta la aplicación:
```bash
   py main.py
```
 
> **Nota:** `pykakasi`, `toml` y `numpy` son opcionales y están cubiertos por `pip install -r requirements.txt` (ver [requirements.txt](./requirements.txt)) — la app funciona sin ellos, solo que sin generación automática de hiragana ni auto-detección de BPM. `madmom` (necesario para la auto-detección de BPM, junto con `numpy`) **no** está disponible en PyPI en estado instalable y se dejó fuera de `requirements.txt` a propósito — instálalo manualmente desde [github.com/CPJKU/madmom](https://github.com/CPJKU/madmom) si quieres esa función.
 
---
 
## Uso paso a paso
 
1. **Inicia** la aplicación y elige el idioma de la interfaz en **Ajustes** si lo necesitas.
2. Ingresa el **Pack Name** y, opcionalmente, el **nombre en japonés**.
3. **Agrega canciones:**
   * Haz clic en **Add Song** para abrir el editor.
   * Completa **Información básica** (usa la calculadora de BPM si no conoces el tempo).
   * Configura las **Dificultades** y sus códigos de nivel válidos.
   * Asigna los **Intérpretes**.
   * Completa **Song Info** y **Letras** (opcional).
   * Define **Variantes de audio** y **SFX** si lo necesitas.
   * Haz clic en **Accept** para guardar la canción.
4. **Administra** la lista: selecciona una canción y usa **Edit** o **Delete**.
5. Opcionalmente, explora los **mods instalados** para reutilizar o revisar canciones de otros packs.
6. Ejecuta **Validate Media Files** para confirmar que no falte nada, y **Create Missing Folders** para armar la estructura de carpetas de tu mod.
7. Guarda tu proyecto cuando quieras con **Save Configuration** (`.pdpack`).
8. Cuando esté listo, haz clic en **Generate File** para exportar `mod_pv_db.txt`.
---
 
## Configuración y autoguardado
 
* **Autoguardado:** cada 5 minutos se guarda un `.pdpack` cifrado en la carpeta `Autosaves/` (máximo 60 archivos).
* **Guardar/cargar manual:** usa **Save Configuration** / **Load Configuration** para archivos de proyecto cifrados; los formatos `.pdpack` antiguos se migran automáticamente.
* **Load Autosave:** restaura rápidamente desde una copia reciente.
---
 
## Exportar `mod_pv_db.txt`
 
1. Verifica que el **Pack Name** esté definido y que exista al menos una canción.
2. Haz clic en **Generate File**.
3. Elige un nombre de archivo (por defecto `mod_pv_db.txt`) y el destino.
4. Se genera un `mod_pv_db.txt` en UTF-8 con la definición completa del pack.
5. Puedes volver a importar ese mismo archivo más adelante con **Import mod_pv_db.txt** para seguir editándolo.
---
 
## Estructura del proyecto
 
```text
MikuMikuDB-Editor/
├── main.py                  # Punto de entrada
├── core/                    # Lógica de la app: cifrado, PV IDs, reproducción, formato pv_db, etc.
├── ui/
│   ├── dialogs/              # Editor de canciones, calculadora de BPM, explorador de mods, etc.
│   ├── widgets/               # Barra de reproducción/seek y otros widgets compartidos
│   └── main_window.py
├── localization/             # Carga de idiomas (data/lang.json)
├── data/                     # Ajustes, catálogo de canciones vanilla, textos de idiomas
├── pv_ids/                   # Caché de PV IDs usados/reservados/libres
├── standalone_scripts/        # Decryptor Tool de .pdpack independiente, herramientas varias
├── docs/guide.md              # Guía de usuario dentro de la app
├── tests/                     # Suite de pruebas de regresión
└── Autosaves/                 # Archivos .pdpack autoguardados
```
 
---
 
## Licencia
 
Este proyecto se publica bajo la **Licencia MIT**. Consulta [LICENSE](./LICENSE) para más detalles.
 
Este proyecto incluye componentes de terceros bajo sus propias licencias (incluyendo una dependencia LGPLv3 y otra GPLv3). Consulta [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md) para la lista completa.
 
---
 
## Agradecimientos
 
* Inspirado en la vibrante comunidad de modding de Project Diva.
* Desarrollado y mantenido por **NyxC**.
* Gracias especiales a todos los beta testers y colaboradores, en especial por su paciencia durante la reescritura de la 2.0.
![Rin Fuwapuchi](images/rin_fuwapuchi.png)
