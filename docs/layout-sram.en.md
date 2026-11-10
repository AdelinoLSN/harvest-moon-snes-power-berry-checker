# SRAM Fields Used by the Checker

[Versão em português brasileiro](layout-sram.md)

[Versión en español](layout-sram.es.md)

The examined `.srm` has two `0x1000`-byte slots, based at `0x0000` and `0x1000`. The offsets below are relative to the selected slot's start.

## Slot validation

| Offset | Size | Field |
|---:|---:|---|
| `+0x2E` | 1 byte | Most-recent-slot marker (`01` in the selected slot). |
| `+0x2F` | 2 bytes | Little-endian checksum. The calculation sums 16-bit words and excludes the marker and checksum itself. |
| `+0x3C` | 4 bytes | ASCII signature `FARM`. |

The program skips incomplete slots, slots without the signature, and slots with an invalid checksum.

## Counter and tools

| Offset | Size | Interpretation |
|---:|---:|---|
| `+0x0E` | 1 byte | Maximum stamina. |
| `+0x0F` | 1 byte | Equipped tool ID. Blue Diamond: `$17`. |
| `+0x17` | 1 byte | `nPowerBerryEaten`, the number of berries eaten. |
| `+0x1A` | 1 byte | Second tool ID. Blue Diamond: `$17`. |
| `+0x84`–`+0x87` | 4 bytes | Four bit rows for items stored in the shed. |
| `+0x86` bit `$40` | 1 bit | Blue Diamond stored in the shed. |

The diamond is considered available if any of these states is present: equipped tool ID equals `$17`, second tool ID equals `$17`, or `slot+0x86 & 0x40 != 0`.

## Event flags

The flags are little-endian words at `+0x60`, `+0x62`, `+0x64`, `+0x66`, `+0x70`, `+0x72`, `+0x74`, and `+0x76`, corresponding to `event1`–`event8`. The checker uses only the masks listed in [the study](estudo.en.md); these mark specific branches and are not a universal list of berries obtained.

## WRAM addresses and SRAM offsets are different

Addresses such as `$7F:1F64` are WRAM addresses observed in Mesen. The save serializes these states into fields within a slot. For events, the relationship used by the program comes from the game's load/save routine; therefore, the file offset shown here is `slot+...`, not a mechanically converted WRAM address.
