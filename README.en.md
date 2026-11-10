# Harvest Moon SNES Power Berry Checker

[Versão em português brasileiro](README.md)

[Versión en español](README.es.md)

A Python tool that reads a **Harvest Moon for SNES** SRAM save (`.srm`) and reports event markers associated with Power Berries. It also checks the Blue Diamond state, which can help infer whether the Winter Flower scene has been triggered if the item is known to have been obtained previously.

The [HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES) decompilation project served as a guide for locating and interpreting routines and fields. The saves used in the study came from a regular game ROM that has been publicly available for years, not from a build of that project. The checker reads ordinary SRAM (`.srm`) saves; analysis does not require a ROM compiled from the disassembly. Findings are inferences from the game version and saves examined, not guarantees for every game revision or save condition.

## Requirements

- Python 3.10 or later
- An 8 KiB `.srm` file containing the game's save slots

There are no external dependencies.

## Usage

```sh
python3 tools/check_power_berry_events.py "/path/to/Harvest Moon.srm"
```

Report messages are printed in Brazilian Portuguese by default. Pass `--english` to print them in English:

```sh
python3 tools/check_power_berry_events.py "/path/to/Harvest Moon.srm" --english
```

The program validates the checksums and selects the slot marked as the most recent save by default. To choose a slot explicitly:

```sh
python3 tools/check_power_berry_events.py "/path/to/Harvest Moon.srm" --slot 0
python3 tools/check_power_berry_events.py "/path/to/Harvest Moon.srm" --slot 1
```

The report classifies known persistent markers as present or absent and displays relevant Blue Diamond fields. The save file is never modified.

## Interpreting the Winter Flower

No persistent bit dedicated to the scene was found. The inference uses the inventory: before use, the Blue Diamond appears in a tool slot or in the shed; the routine that starts the scene consumes it. Therefore, if it is known that the save previously had the diamond, its absence suggests that it was used in this scene.

An isolated `.srm` file cannot distinguish “consumed” from “never obtained.” Cheats that restore items also change the interpretation. The checker explains this limitation in its output.

## Study documentation

- [History, methods, results, and limitations](docs/estudo.en.md)
- [SRAM fields used by the checker](docs/layout-sram.en.md)
- [Histórico, método, resultados e limitações (PT-BR)](docs/estudo.md)
- [Campos do SRAM usados pelo verificador (PT-BR)](docs/layout-sram.md)
- [Study: history, methods, results, and limitations (ES)](docs/estudio.es.md)
- [SRAM fields used by the checker (ES)](docs/layout-sram.es.md)

## Reverse-engineering basis

This is not an official game tool. The disassembly and data maintained in [dzik87/HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES) were used as reverse-engineering references, not as a required source for the saves. See [docs/estudo.en.md](docs/estudo.en.md) for the consulted code paths, Mesen/ImHex observations, and experimental results.
