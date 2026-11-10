# Harvest Moon SNES Power Berry Checker

[Versión en portugués brasileño](README.md) | [English version](README.en.md)

Herramienta en Python para leer una partida SRAM (`.srm`) de **Harvest Moon para SNES** y mostrar marcadores de eventos relacionados con las Power Berries. También comprueba el estado del diamante azul, que permite inferir si ya se activó la escena de la Flor de Invierno cuando se sabe que el objeto se obtuvo anteriormente.

El proyecto de descompilación [HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES) sirvió como guía para localizar e interpretar rutinas y campos. Las partidas usadas en el estudio proceden de una ROM normal del juego, disponible públicamente desde hace años, y no de una compilación de ese proyecto. El verificador lee partidas SRAM normales (`.srm`); el análisis no requiere una ROM compilada a partir del código desensamblado. Las conclusiones son inferencias basadas en la versión y las partidas analizadas, no garantías para todas las revisiones del juego o condiciones de guardado.

## Requisitos

- Python 3.10 o posterior
- Un archivo `.srm` de 8 KiB con las ranuras de guardado del juego

No hay dependencias externas.

## Uso

```sh
python3 tools/check_power_berry_events.py "/ruta/a/Harvest Moon.srm"
```

Los mensajes del informe aparecen en portugués brasileño de forma predeterminada. Usa `--english` para mostrarlos en inglés:

```sh
python3 tools/check_power_berry_events.py "/ruta/a/Harvest Moon.srm" --english
```

De forma predeterminada, el programa valida los checksums y selecciona la ranura marcada como la más reciente. Para elegir una ranura explícitamente:

```sh
python3 tools/check_power_berry_events.py "/ruta/a/Harvest Moon.srm" --slot 0
python3 tools/check_power_berry_events.py "/ruta/a/Harvest Moon.srm" --slot 1
```

El informe clasifica los marcadores persistentes conocidos como presentes o ausentes e indica los campos relevantes del diamante azul. No modifica la partida.

## Interpretación de la Flor de Invierno

No se encontró un bit persistente dedicado a la escena. La inferencia se basa en el inventario: antes de usarse, el diamante azul aparece en una ranura de herramientas o en el almacén; la rutina que inicia la escena lo consume. Por tanto, si se sabe que la partida tuvo el diamante, su ausencia sugiere que se usó en esta escena.

Un archivo `.srm` aislado no permite distinguir entre “consumido” y “nunca obtenido”. Los trucos que restauran objetos también cambian la interpretación. El verificador explica esta limitación.

## Documentación del estudio

- [Estudio: historial, método, resultados y limitaciones](docs/estudio.es.md)
- [Campos SRAM usados por el verificador](docs/layout-sram.es.md)

## Base de ingeniería inversa

Este programa no es una herramienta oficial del juego. El código desensamblado y los datos de [dzik87/HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES) se usaron como referencias para la ingeniería inversa, no como origen obligatorio de las partidas. Consulta [docs/estudio.es.md](docs/estudio.es.md) para ver las rutas de código consultadas, las observaciones en Mesen/ImHex y los resultados experimentales.
