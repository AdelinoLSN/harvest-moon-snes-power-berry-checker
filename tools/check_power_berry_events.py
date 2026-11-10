#!/usr/bin/env python3
"""Check known Harvest Moon SNES Power Berry event markers in an .srm file."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SLOT_SIZE = 0x1000
SLOT_BASES = (0x0000, 0x1000)
FARM_SIGNATURE_OFFSET = 0x3C
MARKER_OFFSET = 0x2E
CHECKSUM_OFFSET = 0x2F

# Save fields for the Blue Diamond: equipped tool, second tool, and shed inventory.
# Campos do save para o diamante azul: ferramenta equipada, segunda ferramenta e depósito.
EQUIPPED_TOOL_OFFSET = 0x0F
SECOND_TOOL_OFFSET = 0x1A
SHED_ROW3_OFFSET = 0x86
BLUE_DIAMOND_ID = 0x17
BLUE_DIAMOND_SHED_MASK = 0x40


EVENTS = (
    ("chicken_statue", 0x60, 0x0200, 0x7F1F64),
    ("first_hoe_find", 0x60, 0x0800, 0x7F1F64),
    ("second_hoe_find", 0x60, 0x1000, 0x7F1F64),
    ("axe_find", 0x60, 0x0400, 0x7F1F64),
    ("autumn_merchant", 0x62, 0x4000, 0x7F1F66),
    ("water_spirit", 0x62, 0x2000, 0x7F1F66),
    ("cave_gnomes", 0x64, 0x2000, 0x7F1F68),
    ("egg_hunt", 0x70, 0x3C00, 0x7F1F6C),
    ("harvest_festival", 0x70, 0x8000, 0x7F1F6C),
)

TEXT = {
    "pt": {
        "description": "Verifica marcadores conhecidos dos eventos de Power Berry em um save .srm.",
        "srm_help": "caminho do arquivo .srm",
        "slot_help": "slot a ler; auto seleciona o slot com marcador de save mais recente (padrão)",
        "ignored_slot": "Slot {index}: ignorado ({reason}).",
        "slot_incomplete": "slot incompleto",
        "farm_missing": "assinatura FARM ausente",
        "checksum_invalid": "checksum inválido (gravado {expected:04X}, calculado {actual:04X})",
        "invalid_slot": "slot {index} inválido: {reason}",
        "no_valid_slot": "nenhum slot válido encontrado",
        "ambiguous_slot": "não foi possível escolher o slot mais recente; use --slot 0 ou --slot 1",
        "file_too_small": "arquivo pequeno demais ({size:#x} bytes; esperado ao menos {expected:#x})",
        "file": "Arquivo: {path}",
        "selected_slot": "Slot selecionado: {index} (base {base:#06x}; marcador {marker:02X})",
        "marker_note": "O status indica a presença do marcador no save, não necessariamente a obtenção ou o consumo do item.",
        "marker_present": "MARCADOR PRESENTE",
        "marker_absent": "SEM MARCADOR",
        "imhex": "  ImHex: slot+{offset:#04x}, valor {value:04X}, máscara {mask:04X}",
        "mesen": "  Mesen: WRAM ${wram:06X} (offset ${offset:05X}), {meaning}",
        "winter_available": "DIAMANTE AINDA DISPONÍVEL (não consumido)",
        "winter_missing": "DIAMANTE AUSENTE (uso da cena da flor inferido)",
        "winter_header": "Flor de Inverno / diamante azul: {status}",
        "winter_fields": "  ImHex: ferramenta equipada slot+{equipped_offset:#04x}={equipped:02X}, segunda ferramenta slot+{second_offset:#04x}={second:02X}; depósito slot+{shed_offset:#04x}={shed:02X} (máscara do diamante {mask:02X})",
        "winter_inference": "  Inferência baseada na mecânica confirmada: o diamante é consumido ao acionar a cena. A ausência indica uso se o save já tinha o diamante; sem histórico, também pode significar que nunca foi obtido.",
        "error": "Erro: {message}",
        "events": {
            "chicken_statue": ("Estátua da galinha", "O script da Power Berry foi iniciado; o bit só é marcado no ramo do achado extra."),
            "first_hoe_find": ("Achado com enxada 1", "Marcador do primeiro achado raro com enxada."),
            "second_hoe_find": ("Achado com enxada 2", "Marcador do segundo achado raro com enxada."),
            "axe_find": ("Achado com machado", "Marcador do achado raro associado ao machado."),
            "autumn_merchant": ("Oferta do mercador do Outono", "Confirma que a oferta foi iniciada; não confirma que a troca foi aceita."),
            "water_spirit": ("Peixe devolvido / espírito da água", "Confirma o evento de soltar o peixe; o script faz aparecer a Power Berry."),
            "cave_gnomes": ("Evento dos duendes na caverna", "Confirma a cena dos duendes associada à entrega da foice."),
            "egg_hunt": ("Caça aos ovos: prêmio registrado", "Qualquer bit A-D confirma um ramo de prêmio; os bits não indicam qual berry foi obtida."),
            "harvest_festival": ("Festival da Colheita", "Marcador do ramo do festival que incrementa o contador geral de berries."),
        },
    },
    "en": {
        "description": "Check known Power Berry event markers in a Harvest Moon SNES .srm save.",
        "srm_help": "path to the .srm save file",
        "slot_help": "slot to read; auto selects the slot marked as most recently saved (default)",
        "ignored_slot": "Slot {index}: skipped ({reason}).",
        "slot_incomplete": "incomplete slot",
        "farm_missing": "FARM signature is missing",
        "checksum_invalid": "invalid checksum (stored {expected:04X}, calculated {actual:04X})",
        "invalid_slot": "slot {index} is invalid: {reason}",
        "no_valid_slot": "no valid save slot found",
        "ambiguous_slot": "could not determine the most recent slot; use --slot 0 or --slot 1",
        "file_too_small": "file is too small ({size:#x} bytes; at least {expected:#x} expected)",
        "file": "File: {path}",
        "selected_slot": "Selected slot: {index} (base {base:#06x}; marker {marker:02X})",
        "marker_note": "Status shows whether a marker is present in the save; it does not necessarily mean the item was obtained or consumed.",
        "marker_present": "MARKER PRESENT",
        "marker_absent": "NO MARKER",
        "imhex": "  ImHex: slot+{offset:#04x}, value {value:04X}, mask {mask:04X}",
        "mesen": "  Mesen: WRAM ${wram:06X} (offset ${offset:05X}), {meaning}",
        "winter_available": "DIAMOND STILL AVAILABLE (not consumed)",
        "winter_missing": "DIAMOND NOT FOUND (flower scene use inferred)",
        "winter_header": "Winter Flower / Blue Diamond: {status}",
        "winter_fields": "  ImHex: equipped tool slot+{equipped_offset:#04x}={equipped:02X}, second tool slot+{second_offset:#04x}={second:02X}; shed slot+{shed_offset:#04x}={shed:02X} (diamond mask {mask:02X})",
        "winter_inference": "  Inference based on confirmed mechanics: the diamond is consumed when the scene starts. Its absence suggests use if the save previously had the diamond; without that history, it may also mean it was never obtained.",
        "error": "Error: {message}",
        "events": {
            "chicken_statue": ("Chicken statue", "The Power Berry script was started; this bit is set only on the extra-find branch."),
            "first_hoe_find": ("Hoe find 1", "Marker for the first rare hoe find."),
            "second_hoe_find": ("Hoe find 2", "Marker for the second rare hoe find."),
            "axe_find": ("Axe find", "Marker for the rare find associated with the axe."),
            "autumn_merchant": ("Autumn merchant offer", "Confirms the offer was started; it does not confirm the trade was accepted."),
            "water_spirit": ("Returned fish / water spirit", "Confirms the fish-release event; its script makes the Power Berry appear."),
            "cave_gnomes": ("Cave gnome event", "Confirms the gnome scene associated with delivering the sickle."),
            "egg_hunt": ("Egg hunt: prize recorded", "Any A-D bit confirms a prize branch; the bits do not identify which berry was obtained."),
            "harvest_festival": ("Harvest Festival", "Marker for the festival branch that increments the overall berry counter."),
        },
    },
}


def read_word(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def valid_slot(data: bytes, base: int, messages: dict[str, object]) -> tuple[bool, str]:
    slot = data[base : base + SLOT_SIZE]
    if len(slot) != SLOT_SIZE:
        return False, str(messages["slot_incomplete"])
    if slot[FARM_SIGNATURE_OFFSET : FARM_SIGNATURE_OFFSET + 4] != b"FARM":
        return False, str(messages["farm_missing"])

    expected = read_word(slot, CHECKSUM_OFFSET)
    check_data = bytearray(slot)
    check_data[MARKER_OFFSET] = 0
    check_data[CHECKSUM_OFFSET : CHECKSUM_OFFSET + 2] = b"\0\0"
    actual = sum(
        int.from_bytes(check_data[index : index + 2], "little")
        for index in range(0, SLOT_SIZE, 2)
    ) & 0xFFFF
    if actual != expected:
        return False, str(messages["checksum_invalid"]).format(expected=expected, actual=actual)
    return True, "ok"


def choose_slot(data: bytes, requested: str, messages: dict[str, object]) -> int:
    candidates = []
    for index, base in enumerate(SLOT_BASES):
        is_valid, reason = valid_slot(data, base, messages)
        if is_valid:
            candidates.append(index)
        elif requested == "auto":
            print(str(messages["ignored_slot"]).format(index=index, reason=reason))

    if requested != "auto":
        index = int(requested)
        is_valid, reason = valid_slot(data, SLOT_BASES[index], messages)
        if not is_valid:
            raise ValueError(str(messages["invalid_slot"]).format(index=index, reason=reason))
        return index

    if not candidates:
        raise ValueError(str(messages["no_valid_slot"]))

    latest = [index for index in candidates if data[SLOT_BASES[index] + MARKER_OFFSET] == 1]
    if len(latest) == 1:
        return latest[0]
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError(str(messages["ambiguous_slot"]))


def check_save(path: Path, requested_slot: str, language: str) -> int:
    messages = TEXT[language]
    data = path.read_bytes()
    if len(data) < 2 * SLOT_SIZE:
        raise ValueError(
            str(messages["file_too_small"]).format(
                size=len(data), expected=2 * SLOT_SIZE
            )
        )

    slot_index = choose_slot(data, requested_slot, messages)
    base = SLOT_BASES[slot_index]
    slot = data[base : base + SLOT_SIZE]

    print(str(messages["file"]).format(path=path))
    print(
        str(messages["selected_slot"]).format(
            index=slot_index, base=base, marker=slot[MARKER_OFFSET]
        )
    )
    print(str(messages["marker_note"]) + "\n")

    event_text = messages["events"]
    assert isinstance(event_text, dict)
    for event_id, offset, mask, wram in EVENTS:
        value = read_word(slot, offset)
        is_present = bool(value & mask)
        label, meaning = event_text[event_id]
        status = str(messages["marker_present"] if is_present else messages["marker_absent"])
        print(
            f"{label}: {status}\n"
            + str(messages["imhex"]).format(offset=offset, value=value, mask=mask)
            + "\n"
            + str(messages["mesen"]).format(
                wram=wram, offset=wram - 0x7E0000, meaning=meaning
            )
        )

    equipped = slot[EQUIPPED_TOOL_OFFSET]
    second = slot[SECOND_TOOL_OFFSET]
    shed_row3 = slot[SHED_ROW3_OFFSET]
    diamond_available = (
        equipped == BLUE_DIAMOND_ID
        or second == BLUE_DIAMOND_ID
        or bool(shed_row3 & BLUE_DIAMOND_SHED_MASK)
    )
    winter_status = str(
        messages["winter_available"] if diamond_available else messages["winter_missing"]
    )
    print(
        str(messages["winter_header"]).format(status=winter_status)
        + "\n"
        + str(messages["winter_fields"]).format(
            equipped_offset=EQUIPPED_TOOL_OFFSET,
            equipped=equipped,
            second_offset=SECOND_TOOL_OFFSET,
            second=second,
            shed_offset=SHED_ROW3_OFFSET,
            shed=shed_row3,
            mask=BLUE_DIAMOND_SHED_MASK,
        )
        + "\n"
        + str(messages["winter_inference"])
    )
    return 0


def main() -> int:
    default_messages = TEXT["pt"]
    parser = argparse.ArgumentParser(description=str(default_messages["description"]))
    parser.add_argument("srm", type=Path, help=str(default_messages["srm_help"]))
    parser.add_argument(
        "--slot",
        choices=("auto", "0", "1"),
        default="auto",
        help=str(default_messages["slot_help"]),
    )
    parser.add_argument(
        "--english",
        action="store_true",
        help="print report messages in English (default: Brazilian Portuguese)",
    )
    arguments = parser.parse_args()
    language = "en" if arguments.english else "pt"

    try:
        return check_save(arguments.srm, arguments.slot, language)
    except (OSError, ValueError) as error:
        print(str(TEXT[language]["error"]).format(message=error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
