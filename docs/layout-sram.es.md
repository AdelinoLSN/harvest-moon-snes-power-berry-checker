# Campos SRAM usados por el verificador

[Versión en portugués brasileño](layout-sram.md) | [English version](layout-sram.en.md)

El archivo `.srm` analizado tiene dos ranuras de `0x1000` bytes, con bases `0x0000` y `0x1000`. Los offsets siguientes son relativos al inicio de la ranura seleccionada.

## Validación de la ranura

| Offset | Tamaño | Campo |
|---:|---:|---|
| `+0x2E` | 1 byte | Marca de la ranura guardada más recientemente (`01` en la ranura seleccionada). |
| `+0x2F` | 2 bytes | Checksum little-endian. El cálculo suma palabras de 16 bits y excluye la marca y el propio checksum. |
| `+0x3C` | 4 bytes | Firma ASCII `FARM`. |

El programa omite las ranuras incompletas, sin firma o con un checksum no válido.

## Contador y herramientas

| Offset | Tamaño | Interpretación |
|---:|---:|---|
| `+0x0E` | 1 byte | Resistencia máxima. |
| `+0x0F` | 1 byte | ID de la herramienta equipada. Diamante azul: `$17`. |
| `+0x17` | 1 byte | `nPowerBerryEaten`, contador de berries consumidas. |
| `+0x1A` | 1 byte | ID de la segunda herramienta. Diamante azul: `$17`. |
| `+0x84`–`+0x87` | 4 bytes | Cuatro filas de bits para los objetos del cobertizo. |
| `+0x86` bit `$40` | 1 bit | Diamante azul guardado en el cobertizo. |

Se considera que el diamante sigue disponible si se cumple cualquiera de estas condiciones: la herramienta equipada tiene ID `$17`, la segunda herramienta tiene ID `$17` o `slot+0x86 & 0x40 != 0`.

## Marcas de eventos

Las marcas son palabras little-endian en `+0x60`, `+0x62`, `+0x64`, `+0x66`, `+0x70`, `+0x72`, `+0x74` y `+0x76`, correspondientes a `event1`–`event8`. El verificador usa solo las máscaras indicadas en [el estudio](estudio.es.md); son marcas de ramas específicas, no una lista universal de berries obtenidas.

## Las direcciones WRAM y los offsets SRAM son distintos

Direcciones como `$7F:1F64` son direcciones de WRAM observadas en Mesen. La partida serializa estos estados en campos de una ranura. Para los eventos, la relación que usa el programa procede de la rutina de carga/guardado del juego; por tanto, el offset del archivo indicado aquí es `slot+...`, no una conversión mecánica de una dirección WRAM.
