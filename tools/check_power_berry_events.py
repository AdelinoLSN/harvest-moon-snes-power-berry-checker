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
EQUIPPED_TOOL_OFFSET = 0x0F
SECOND_TOOL_OFFSET = 0x1A
SHED_ROW3_OFFSET = 0x86
BLUE_DIAMOND_ID = 0x17
BLUE_DIAMOND_SHED_MASK = 0x40


EVENTS = (
    ("Estátua da galinha", 0x60, 0x0200, 0x7F1F64,
     "O script da Power Berry foi iniciado; o bit só é marcado no ramo do achado extra."),
    ("Achado com enxada 1", 0x60, 0x0800, 0x7F1F64,
     "Marcador do primeiro achado raro com enxada."),
    ("Achado com enxada 2", 0x60, 0x1000, 0x7F1F64,
     "Marcador do segundo achado raro com enxada."),
    ("Achado com machado", 0x60, 0x0400, 0x7F1F64,
     "Marcador do achado raro associado ao machado."),
    ("Oferta do mercador do Outono", 0x62, 0x4000, 0x7F1F66,
     "Confirma que a oferta foi iniciada; não confirma que a troca foi aceita."),
    ("Peixe devolvido / espírito da água", 0x62, 0x2000, 0x7F1F66,
     "Confirma o evento de soltar o peixe; o script faz aparecer a Power Berry."),
    ("Evento dos duendes na caverna", 0x64, 0x2000, 0x7F1F68,
     "Confirma a cena dos duendes associada à entrega da foice."),
    ("Caça aos ovos: prêmio registrado", 0x70, 0x3C00, 0x7F1F6C,
     "Qualquer bit A-D confirma um ramo de prêmio; os bits não indicam qual berry foi obtida."),
    ("Festival da Colheita", 0x70, 0x8000, 0x7F1F6C,
     "Marcador do ramo do festival que incrementa o contador geral de berries."),
)


def read_word(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def valid_slot(data: bytes, base: int) -> tuple[bool, str]:
    slot = data[base : base + SLOT_SIZE]
    if len(slot) != SLOT_SIZE:
        return False, "slot incompleto"
    if slot[FARM_SIGNATURE_OFFSET : FARM_SIGNATURE_OFFSET + 4] != b"FARM":
        return False, "assinatura FARM ausente"

    expected = read_word(slot, CHECKSUM_OFFSET)
    check_data = bytearray(slot)
    check_data[MARKER_OFFSET] = 0
    check_data[CHECKSUM_OFFSET : CHECKSUM_OFFSET + 2] = b"\0\0"
    actual = sum(
        int.from_bytes(check_data[i : i + 2], "little")
        for i in range(0, SLOT_SIZE, 2)
    ) & 0xFFFF
    if actual != expected:
        return False, f"checksum inválido (gravado {expected:04X}, calculado {actual:04X})"
    return True, "ok"


def choose_slot(data: bytes, requested: str) -> int:
    candidates = []
    for index, base in enumerate(SLOT_BASES):
        ok, reason = valid_slot(data, base)
        if ok:
            candidates.append(index)
        elif requested == "auto":
            print(f"Slot {index}: ignorado ({reason}).")

    if requested != "auto":
        index = int(requested)
        ok, reason = valid_slot(data, SLOT_BASES[index])
        if not ok:
            raise ValueError(f"slot {index} inválido: {reason}")
        return index

    if not candidates:
        raise ValueError("nenhum slot válido encontrado")

    latest = [i for i in candidates if data[SLOT_BASES[i] + MARKER_OFFSET] == 1]
    if len(latest) == 1:
        return latest[0]
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError("não foi possível escolher o slot mais recente; use --slot 0 ou --slot 1")


def check_save(path: Path, requested_slot: str) -> int:
    data = path.read_bytes()
    if len(data) < 2 * SLOT_SIZE:
        raise ValueError(f"arquivo pequeno demais ({len(data):#x} bytes; esperado ao menos {2 * SLOT_SIZE:#x})")

    slot_index = choose_slot(data, requested_slot)
    base = SLOT_BASES[slot_index]
    slot = data[base : base + SLOT_SIZE]

    print(f"Arquivo: {path}")
    print(f"Slot selecionado: {slot_index} (base {base:#06x}; marcador {slot[MARKER_OFFSET]:02X})")
    print("Status indica presença do marcador no save, não necessariamente obtenção/consumo do item.\n")

    for label, offset, mask, wram, meaning in EVENTS:
        value = read_word(slot, offset)
        present = bool(value & mask)
        status = "MARCADOR PRESENTE" if present else "SEM MARCADOR"
        print(
            f"{label}: {status}\n"
            f"  ImHex: slot+{offset:#04x}, valor {value:04X}, máscara {mask:04X}\n"
            f"  Mesen: WRAM ${wram:06X} (offset ${wram - 0x7E0000:05X}), {meaning}"
        )

    equipped = slot[EQUIPPED_TOOL_OFFSET]
    second = slot[SECOND_TOOL_OFFSET]
    shed_row3 = slot[SHED_ROW3_OFFSET]
    diamond_available = (
        equipped == BLUE_DIAMOND_ID
        or second == BLUE_DIAMOND_ID
        or bool(shed_row3 & BLUE_DIAMOND_SHED_MASK)
    )
    if diamond_available:
        winter_status = "DIAMANTE AINDA DISPONÍVEL (não consumido)"
    else:
        winter_status = "DIAMANTE AUSENTE (uso da cena da flor inferido)"
    print(
        f"Flor de Inverno / diamante azul: {winter_status}\n"
        f"  ImHex: tool equipado slot+{EQUIPPED_TOOL_OFFSET:#04x}="
        f"{equipped:02X}, segundo tool slot+{SECOND_TOOL_OFFSET:#04x}={second:02X}; "
        f"depósito slot+{SHED_ROW3_OFFSET:#04x}={shed_row3:02X} "
        f"(máscara do diamante {BLUE_DIAMOND_SHED_MASK:02X})\n"
        "  Inferência baseada na mecânica confirmada: o diamante é consumido ao acionar a cena. "
        "Ausência indica uso se o save já tinha o diamante; sem histórico, também pode significar que nunca foi obtido."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica os marcadores conhecidos dos eventos de Power Berry em um save .srm."
    )
    parser.add_argument("srm", type=Path, help="caminho do arquivo .srm")
    parser.add_argument(
        "--slot", choices=("auto", "0", "1"), default="auto",
        help="slot a ler; auto seleciona o slot com marcador de save mais recente (padrão)",
    )
    args = parser.parse_args()

    try:
        return check_save(args.srm, args.slot)
    except (OSError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
