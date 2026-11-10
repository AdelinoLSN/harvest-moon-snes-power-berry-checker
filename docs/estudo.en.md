# Study of Power Berry Events

[Versão em português brasileiro](estudo.md)

[Versión en español](estudio.es.md)

## Objective

Identify which events associated with the ten Power Berries appear to have occurred, based on a Harvest Moon for SNES SRAM save. The practical goal is to point out events that may still be untriggered, including cases where the game does not keep an explicit scene flag.

This study combines the [HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES) decompilation project, WRAM inspection in Mesen's Memory Viewer, byte inspection in ImHex, and comparisons of `.srm` files before and after events. The disassembly served as a guide for locating routines, addresses, and fields and for forming code interpretations. The experimental saves came from a regular game ROM that has been publicly available for years, not from a build of the decompilation project. The checker therefore analyzes ordinary game SRAM saves; they do not need to have been created by a ROM compiled from that project. Conclusions are inferences and may depend on the game revision.

## 1. Initial hypothesis: find persistent flags

The first step was to map the energy fields and game flags. Relevant variables found in the disassembly include:

| WRAM | Mesen offset | Identified use |
|---|---:|---|
| `$7E:0917` | `$00917` | Current maximum stamina. The Power Berry consumption routine adds `$0A`. |
| `$7F:1F36` | `$11F36` | `nPowerBerryEaten`, the number of berries eaten. |
| `$7F:1F5A`–`$7F:1F63` | `$11F5A`–`$11F63` | Daily flags; temporary state, not a persistent per-event record. |
| `$7F:1F64`–`$7F:1F73` | `$11F64`–`$11F73` | `event1`–`event8`, permanent flags stored in the save. |

When a Power Berry is eaten, the game increments the counter, raises maximum stamina by 10, and increases happiness. This shows that a berry was eaten, but not which event supplied it. A berry can also be obtained without being eaten automatically.

### Correction to an earlier hypothesis

An initial notes file suggested that `daily1` bit `$0080` might be connected to the Winter Flower. This interpretation was not confirmed and should be treated as incorrect for this checker: daily flags do not provide persistent proof that the flower event occurred. A daily bit should not be used as event history after saving/reloading or advancing the night.

## 2. Persistent markers found

The save has eight event words at `slot+0x60` through `slot+0x76`. The masks below were associated with routines/events in the source code and are used by the checker:

| Event / branch | SRAM field | Mask | What the marker supports | Interpretation limit |
|---|---:|---:|---|---|
| Chicken statue | `slot+0x60` (`event1`) | `0x0200` | Branch associated with the Power Berry script. | The bit records the code branch/script, not necessarily that the item was consumed. |
| Rare hoe find 1 | `slot+0x60` (`event1`) | `0x0800` | First rare hoe-find marker. | Not a universal berry counter. |
| Rare hoe find 2 | `slot+0x60` (`event1`) | `0x1000` | Second rare hoe-find marker. | Same limitation. |
| Axe-associated find | `slot+0x60` (`event1`) | `0x0400` | Marker associated with the axe find. | The association is interpreted from the tool code. |
| Autumn merchant offer | `slot+0x62` (`event2`) | `0x4000` | The offer was started. | Does not prove the trade was accepted. |
| Returned fish / water spirit | `slot+0x62` (`event2`) | `0x2000` | Fish-release event; its associated script makes a berry appear. | Does not prove the berry was eaten. |
| Cave gnome scene | `slot+0x64` (`event3`) | `0x2000` | Scene associated with delivering the sickle. | Its connection to the reward is inferred from the AI flow. |
| Egg hunt | `slot+0x70` (`event5`) | `0x3C00` | At least one of prize branches A–D was recorded. | The bits do not identify which berry or prize was obtained. |
| Harvest Festival | `slot+0x70` (`event5`) | `0x8000` | Festival branch that increments the overall berry counter. | Does not prove later consumption. |

These nine markers cover useful events and branches. Some masks represent event branches rather than a simple count of “berries collected.” The checker preserves this distinction in its output.

## 3. Winter Flower and Blue Diamond

### What the code shows

In the decompilation project, `fToolUsedAction0x17_BlueDiamond` in [`src/code/bank_82/tools.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_82/tools.asm) checks the time, the winter mountain area, and the object ahead. When it finds the expected object (`$F6`), it starts AI script `$12` and clears `toolEquipped`.

The script in [`src/ai/us/scripts/script_12.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/ai/us/scripts/script_12.asm) runs the scene. No dedicated `event1`–`event8` bit was found in this flow to persistently record “Winter Flower completed.” The routine that restores the winter mountaintop area is also empty in [`src/code/bank_81/items_misc.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_81/items_misc.asm).

At first, `STZ toolEquipped` appeared to mean only unequipping the item. Inspection of the storage flow and the player's experiment clarified the interpretation: the diamond is removed from the inventory when used in this scene. Restoring it with Action Replay allowed the event to be repeated and the Power Berry to be obtained again. This empirical evidence supports consumption as the mechanism that prevents normal repetition.

### How inventory is represented in the save

The save format documented in `src/code/bank_83/game_engine.asm` stores:

- equipped tool at `slot+0x0F`;
- second tool at `slot+0x1A`;
- shed inventory at bytes `slot+0x84`–`slot+0x87`.

The `nShedToolPlacementTable` table in [`assets/tables/data/tile_scripts.csv`](https://github.com/dzik87/HarvestMoonSNES/blob/master/assets/tables/data/tile_scripts.csv) maps the Blue Diamond (`EITEM_BLUEDIAMOND`, ID `$17`) to the third shed row byte (`slot+0x86`) and mask `$40`. The item is considered available if it is equipped, in the second tool slot, or in the shed.

Therefore, the diamond's absence can serve as an **indirect marker of the scene**, assuming the save previously had the item. A save file without the item cannot distinguish “consumed” from “never obtained”; the checker qualifies the result as an inference and documents this condition.

## 4. Experimental save comparison

`BEFORE.srm` and `AFTER.srm`, provided by the player, were compared. They were created while playing a regular game ROM that has been publicly available for years, not a build of the decompilation project. Both are 8192 bytes; slot 0 is selected for this analysis. The files are not distributed in this repository.

The player reported that the saves correspond to 02/Winter and 03/Winter, after advancing one day and performing the event/consumption. Observed values in slot 0:

| Field | Before | After | Interpretation |
|---|---:|---:|---|
| `slot+0x17`, berries eaten | `0x08` | `0x09` | Increased from 8 to 9. |
| `slot+0x0E`, maximum stamina | `0xB4` (180) | `0xBE` (190) | Increase of 10, consistent with eating one berry. |
| `slot+0x86`, third shed row | `0x5E` | `0x1F` | Blue Diamond bit `$40` was set, then cleared. |
| `slot+0x1A`, second tool | `0x0E` | `0x0E` | No change. |
| `event1`–`event8` words | no change in relevant fields | no change in relevant fields | No new persistent flag identified the flower event. |

The checksum validated was for slot 0. Slot 1 was skipped because its checksum was invalid. The combination “diamond bit cleared + berry counter increased by 1 + maximum stamina increased by 10,” along with the player's confirmation that the Winter Power Berry was eaten during this interval, is strong evidence that the item was used and the berry was eaten. Since the interval also included a day advance and other data changed, not every changed byte is attributed exclusively to the scene.

## 5. Method and limitations

1. Consult disassembly writers/readers for energy variables, event flags, tools, and save data.
2. Inspect candidate addresses in Mesen's Memory Viewer during gameplay.
3. Compare WRAM values with `.srm` bytes using the slot layout and little-endian byte order.
4. Validate the slot checksum and marker before interpreting data.
5. Compare controlled saves before and after, then cross-check deltas against a known gameplay sequence.

Known limitations:

- This is reverse-engineering analysis, not an official Nintendo specification.
- The disassembly may have gaps or provisional routine names; a bit/event association can be revised.
- Branch flags do not guarantee that an item was actually collected, kept, or consumed.
- A missing diamond in one save does not prove prior possession. Cheats, save editing, or another external loss invalidate the inference.
- `nPowerBerryEaten` does not identify the berry's source.
- Results may differ across regional/game revisions, ROM hacks, patches, and emulator-specific behavior.
- The analysis should be repeated using saves from the revision intended for support.

## Code references

- Decompilation project: [dzik87/HarvestMoonSNES](https://github.com/dzik87/HarvestMoonSNES)
- Blue Diamond flow: [`tools.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_82/tools.asm)
- Flower AI scene: [`script_12.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/ai/us/scripts/script_12.asm)
- Save read/write: [`game_engine.asm`](https://github.com/dzik87/HarvestMoonSNES/blob/master/src/code/bank_83/game_engine.asm)
- Shed bits: [`tile_scripts.csv`](https://github.com/dzik87/HarvestMoonSNES/blob/master/assets/tables/data/tile_scripts.csv)
