# Estudio de los eventos de Power Berry

[Versión en portugués brasileño](estudo.md) | [English version](estudo.en.md)

## Objetivo

Identificar, a partir de una partida SRAM de Harvest Moon para SNES, qué eventos relacionados con las diez Power Berries parecen haber ocurrido. El objetivo práctico es señalar eventos que quizá aún no se hayan activado, incluso cuando el juego no guarda una marca explícita de la escena.

El estudio combina el proyecto de descompilación [HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES), la inspección de WRAM con Memory Viewer de Mesen, la lectura de bytes en ImHex y la comparación de archivos `.srm` anteriores y posteriores a los eventos. El código desensamblado sirvió como guía para localizar rutinas, direcciones y campos e interpretar el código. Las partidas experimentales proceden de una ROM normal del juego, disponible públicamente desde hace años, no de una compilación del proyecto de descompilación. Por tanto, el verificador analiza partidas SRAM normales; no es necesario que se hayan creado con una ROM compilada a partir de ese proyecto. Las conclusiones son inferencias y pueden depender de la revisión del juego.

## 1. Hipótesis inicial: localizar marcas persistentes

El primer paso fue mapear los campos de energía y las marcas del juego. Entre las variables relevantes encontradas en el código desensamblado están:

| WRAM | Offset de Mesen | Uso identificado |
|---|---:|---|
| `$7E:0917` | `$00917` | Resistencia máxima actual. La rutina que consume una Power Berry suma `$0A`. |
| `$7F:1F36` | `$11F36` | `nPowerBerryEaten`, contador de berries consumidas. |
| `$7F:1F5A`–`$7F:1F63` | `$11F5A`–`$11F63` | Marcas diarias; estado temporal, no un registro persistente por evento. |
| `$7F:1F64`–`$7F:1F73` | `$11F64`–`$11F73` | `event1`–`event8`, marcas permanentes guardadas en la partida. |

Al consumir una Power Berry, el juego incrementa el contador, aumenta la resistencia máxima en 10 y aumenta la felicidad. Esto indica que se comió una berry, pero no qué evento la proporcionó. También se puede obtener una berry sin consumirla automáticamente.

### Corrección de una hipótesis anterior

Un archivo inicial de notas sugería que el bit `$0080` de `daily1` podía estar relacionado con la Flor de Invierno. Esta interpretación no se confirmó y debe considerarse incorrecta para este verificador: las marcas diarias no prueban de forma persistente que ocurriera el evento de la flor. Tampoco debe usarse un bit diario aislado como historial después de guardar/cargar o avanzar la noche.

## 2. Marcas persistentes encontradas

La partida tiene ocho palabras de eventos entre `slot+0x60` y `slot+0x76`. Las máscaras siguientes se asociaron con rutinas o eventos del código fuente y las usa el programa:

| Evento / rama | Campo SRAM | Máscara | Qué indica la marca | Límite de la interpretación |
|---|---:|---:|---|---|
| Estatua de la gallina | `slot+0x60` (`event1`) | `0x0200` | Rama asociada al script de la Power Berry. | El bit registra la rama o el script, no necesariamente que se consumiera el objeto. |
| Hallazgo raro con azada 1 | `slot+0x60` (`event1`) | `0x0800` | Primera marca de hallazgo raro con azada. | No es un contador universal de berries. |
| Hallazgo raro con azada 2 | `slot+0x60` (`event1`) | `0x1000` | Segunda marca de hallazgo raro con azada. | La misma limitación. |
| Hallazgo asociado al hacha | `slot+0x60` (`event1`) | `0x0400` | Marca asociada al hallazgo con el hacha. | La relación se interpreta a partir del código de la herramienta. |
| Oferta del mercader de otoño | `slot+0x62` (`event2`) | `0x4000` | La oferta se inició. | No demuestra que se aceptara el intercambio. |
| Pez devuelto / espíritu del agua | `slot+0x62` (`event2`) | `0x2000` | Evento de soltar el pez; el script asociado hace aparecer una berry. | No demuestra que se consumiera la berry. |
| Escena de los duendes de la cueva | `slot+0x64` (`event3`) | `0x2000` | Escena asociada a entregar la hoz. | La relación con la recompensa se infiere del flujo de IA. |
| Caza de huevos | `slot+0x70` (`event5`) | `0x3C00` | Se registró alguna de las ramas de premio A–D. | Los bits no identifican qué berry o premio se obtuvo. |
| Festival de la cosecha | `slot+0x70` (`event5`) | `0x8000` | Rama del festival que incrementa el contador general de berries. | No demuestra un consumo posterior. |

Estas nueve marcas cubren eventos y ramas útiles para el análisis. Algunas máscaras representan ramas de eventos, no un recuento simple de “berries recogidas”. El verificador mantiene esta distinción en el resultado.

## 3. Flor de Invierno y diamante azul

### Qué muestra el código

En el proyecto de descompilación, `fToolUsedAction0x17_BlueDiamond` en [`src/code/bank_82/tools.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_82/tools.asm) valida la hora, la zona de la montaña invernal y el objeto que está delante. Al encontrar el objeto esperado (`$F6`), inicia el script de IA `$12` y pone `toolEquipped` a cero.

El script [`src/ai/us/scripts/script_12.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/ai/us/scripts/script_12.asm) ejecuta la escena. En este flujo no se encontró un bit dedicado de `event1`–`event8` que registre de forma persistente “Flor de Invierno completada”. La rutina que restaura la zona de la cima de la montaña en invierno también está vacía en [`src/code/bank_81/items_misc.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_81/items_misc.asm).

Al principio, `STZ toolEquipped` parecía indicar que el objeto solo se desequipaba. La inspección del flujo de almacenamiento y el experimento del jugador aclararon la interpretación: el diamante se elimina del inventario al usarse en esta escena. Restaurarlo con Action Replay permitió repetir el evento y obtener otra vez la Power Berry. Esta evidencia empírica respalda que el consumo es el mecanismo que impide repetir la escena normalmente.

### Representación del inventario en la partida

El formato de partida documentado en `src/code/bank_83/game_engine.asm` guarda:

- herramienta equipada en `slot+0x0F`;
- segunda herramienta en `slot+0x1A`;
- inventario del cobertizo en los bytes `slot+0x84`–`slot+0x87`.

La tabla `nShedToolPlacementTable`, en [`assets/tables/data/tile_scripts.csv`](https://github.com/dzik87/HarvestMoonSNES/blob/master/assets/tables/data/tile_scripts.csv), asigna el diamante azul (`EITEM_BLUEDIAMOND`, ID `$17`) al byte de la tercera fila del cobertizo (`slot+0x86`) y a la máscara `$40`. Se considera que el objeto está disponible si está equipado, en el segundo espacio o en el cobertizo.

Por tanto, la ausencia del diamante puede servir como **marca indirecta de la escena**, suponiendo que la partida tuvo el objeto anteriormente. Una partida aislada sin el diamante no permite distinguir entre “se consumió” y “nunca se obtuvo”; por eso el programa califica el resultado como una inferencia y explica esta condición.

## 4. Comparación experimental de partidas

Se compararon `BEFORE.srm` y `AFTER.srm`, proporcionados por el jugador y creados al jugar una ROM normal, disponible públicamente desde hace años (no una compilación del proyecto de descompilación). Ambos tienen 8192 bytes; para el análisis se selecciona la ranura 0. Los archivos no se distribuyen en este repositorio.

El jugador indicó que las partidas corresponden a 02/Invierno y 03/Invierno, después de avanzar un día y realizar el evento/consumo. Valores observados en la ranura 0:

| Campo | Antes | Después | Interpretación |
|---|---:|---:|---|
| `slot+0x17`, berries consumidas | `0x08` | `0x09` | Aumentó de 8 a 9. |
| `slot+0x0E`, resistencia máxima | `0xB4` (180) | `0xBE` (190) | Aumento de 10, compatible con consumir una berry. |
| `slot+0x86`, tercera fila del cobertizo | `0x5E` | `0x1F` | El bit `$40` del diamante azul estaba activo y luego se desactivó. |
| `slot+0x1A`, segunda herramienta | `0x0E` | `0x0E` | Sin cambios. |
| palabras `event1`–`event8` | sin cambios en los campos relevantes | sin cambios en los campos relevantes | Ninguna marca persistente nueva identificó el evento de la flor. |

Se validó el checksum de la ranura 0. Se omitió la ranura 1 porque su checksum no era válido. La combinación “bit del diamante eliminado + contador de berries +1 + resistencia máxima +10”, junto con la confirmación del jugador de que consumió la Power Berry de invierno durante ese intervalo, es evidencia sólida de que se usó el objeto y se comió la berry. Como el intervalo también incluyó el avance de un día y cambiaron otros datos, no se atribuye cada byte modificado exclusivamente a la escena.

## 5. Método y limitaciones

1. Consultar en el código desensamblado las rutinas que leen y escriben las variables de energía, las marcas de eventos, las herramientas y los datos de guardado.
2. Inspeccionar direcciones candidatas en el Memory Viewer de Mesen durante el juego.
3. Comparar valores de WRAM con bytes del `.srm` usando el diseño de las ranuras y el orden little-endian.
4. Validar el checksum y la marca de la ranura antes de interpretar los datos.
5. Comparar partidas controladas anteriores y posteriores y relacionar las diferencias con una secuencia de juego conocida.

Limitaciones conocidas:

- Es un análisis de ingeniería inversa, no una especificación oficial de Nintendo.
- El código desensamblado puede tener lagunas o nombres provisionales de rutinas; se puede revisar la asociación entre un bit y un evento.
- Las marcas de rama no garantizan que el objeto se recogiera, se conservara o se consumiera realmente.
- La ausencia del diamante en una sola partida no demuestra que se poseyera antes. Los trucos, la edición de partidas u otra pérdida externa invalidan la inferencia.
- El incremento de `nPowerBerryEaten` no identifica el origen de la berry.
- Los resultados pueden variar entre revisiones regionales, revisiones del juego, hacks de ROM, parches y comportamientos específicos del emulador.
- El análisis debe repetirse con partidas de la revisión que se quiera admitir.

## Referencias del código

- Proyecto de descompilación: [dzik87/HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES)
- Flujo del diamante azul: [`tools.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_82/tools.asm)
- Escena de IA de la flor: [`script_12.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/ai/us/scripts/script_12.asm)
- Lectura/escritura de partidas: [`game_engine.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_83/game_engine.asm)
- Bits del cobertizo: [`tile_scripts.csv`](https://github.com/dzik87/HarvestMoonSNES/blob/master/assets/tables/data/tile_scripts.csv)
