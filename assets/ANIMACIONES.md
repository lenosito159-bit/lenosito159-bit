# Recursos del perfil

Arte original generado localmente; sin rastreadores, servicios de imágenes ni peticiones externas en las animaciones. El README utiliza GIF porque GitHub los reproduce como imágenes normales. Los SVG anteriores se conservan, pero ya no se cargan en el perfil.

| Recurso | Tamaño de imagen | Duración del ciclo | Velocidad |
| --- | --- | --- | --- |
| `galaxy.gif` | 960 × 400 | 4,8 s | 20 fps |
| `orbit-signals.gif` | 560 × 76 | 4,8 s | 20 fps |
| `intro.gif` | 800 × 78 | 11,52 s | Transiciones de 80 ms y pausas de lectura |

Los tres GIF pesan en conjunto aproximadamente **3,54 MiB**. Se utiliza una paleta compartida de 128 colores y compresión de zonas sin cambios. Todos tienen bucle infinito. La galaxia espiral ocupa el fondo, con brazos luminosos que giran, bandas de polvo oscuro y partículas en órbita. El planeta aparece en primer plano sin tapar el núcleo. La galaxia, nebulosas, partículas, planeta, luna e iconos siguen funciones periódicas: el último fotograma continúa en el primero sin reiniciar posiciones. Las frases se desvanecen sobre el mismo fondo entre estados; las pausas conservan su duración al optimizar fotogramas repetidos.

## Accesibilidad y GitHub

El nombre, profesión y enfoque están también en texto. Cada imagen tiene descripción alternativa. Los elementos `picture` seleccionan PNG cuando el navegador y el renderizado de GitHub conservan y admiten `prefers-reduced-motion`. Un GIF por sí solo no puede detectar esa preferencia: [PERFIL-ESTATICO.md](PERFIL-ESTATICO.md) ofrece una alternativa explícita, sin imágenes animadas, incluso si un cliente ignora la selección de `picture`.

No se insertan JavaScript, canvas ni CSS en el Markdown. Los recursos se alojan en este mismo repositorio. Las imágenes se adaptan al ancho disponible mediante el comportamiento de imágenes de GitHub; el texto esencial permanece fuera de las imágenes para mantener su legibilidad en móvil.

## Regeneración

Requisitos utilizados: Python 3.12, Pillow 12.3.0, NumPy 2.3.5 y DejaVu Sans (`fonts-dejavu-core` en Debian/Ubuntu).

Desde la raíz del repositorio:

```sh
python -m venv /tmp/profile-art-venv
/tmp/profile-art-venv/bin/pip install -r assets/requirements-art.txt
/tmp/profile-art-venv/bin/python assets/generate.py
```

No hace falta regenerar los archivos para visualizar el perfil. El generador usa una semilla fija, guarda los GIF y los PNG estáticos y muestra sus pesos. La versión exacta de los tipos de letra y de las bibliotecas de compresión del sistema puede variar los bytes finales sin cambiar el diseño.
