"""Regression tests for the Power Berry save checker."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import check_power_berry_events as checker


def make_valid_slot(marker: int = 0, blue_diamond_in_shed: bool = False) -> bytes:
    """Build a minimal synthetic save slot with a valid checksum."""
    slot = bytearray(checker.SLOT_SIZE)
    slot[checker.FARM_SIGNATURE_OFFSET : checker.FARM_SIGNATURE_OFFSET + 4] = b"FARM"
    slot[checker.MARKER_OFFSET] = marker
    if blue_diamond_in_shed:
        slot[checker.SHED_ROW3_OFFSET] = checker.BLUE_DIAMOND_SHED_MASK

    checksum_data = bytearray(slot)
    checksum_data[checker.MARKER_OFFSET] = 0
    checksum_data[checker.CHECKSUM_OFFSET : checker.CHECKSUM_OFFSET + 2] = b"\0\0"
    checksum = sum(
        int.from_bytes(checksum_data[offset : offset + 2], "little")
        for offset in range(0, checker.SLOT_SIZE, 2)
    ) & 0xFFFF
    slot[checker.CHECKSUM_OFFSET : checker.CHECKSUM_OFFSET + 2] = checksum.to_bytes(
        2, "little"
    )
    return bytes(slot)


def make_save() -> bytes:
    return make_valid_slot(marker=0) + make_valid_slot(marker=1)


class PowerBerryCheckerTests(unittest.TestCase):
    def test_read_word_uses_little_endian(self) -> None:
        self.assertEqual(checker.read_word(b"\x34\x12", 0), 0x1234)

    def test_valid_slot_accepts_signature_and_checksum(self) -> None:
        is_valid, reason = checker.valid_slot(
            make_valid_slot(), 0, checker.TEXT["pt"]
        )
        self.assertTrue(is_valid)
        self.assertEqual(reason, "ok")

    def test_valid_slot_rejects_corrupt_checksum(self) -> None:
        slot = bytearray(make_valid_slot())
        slot[0x60] ^= 0x01
        is_valid, reason = checker.valid_slot(bytes(slot), 0, checker.TEXT["pt"])
        self.assertFalse(is_valid)
        self.assertIn("checksum inválido", reason)

    def test_auto_selection_uses_slot_marked_as_latest(self) -> None:
        self.assertEqual(checker.choose_slot(make_save(), "auto", checker.TEXT["pt"]), 1)

    def test_explicit_slot_selection_is_respected(self) -> None:
        self.assertEqual(checker.choose_slot(make_save(), "0", checker.TEXT["pt"]), 0)

    def test_report_defaults_to_brazilian_portuguese_and_does_not_modify_save(self) -> None:
        save_data = make_save()
        with tempfile.TemporaryDirectory() as directory:
            save_path = Path(directory) / "sample.srm"
            save_path.write_bytes(save_data)
            stdout = StringIO()
            stderr = StringIO()
            with patch("sys.argv", ["checker", str(save_path)]):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    result = checker.main()

            self.assertEqual(result, 0)
            self.assertIn("Arquivo:", stdout.getvalue())
            self.assertIn("Estátua da galinha", stdout.getvalue())
            self.assertIn("Flor de Inverno", stdout.getvalue())
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(save_path.read_bytes(), save_data)

    def test_english_flag_localizes_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            save_path = Path(directory) / "sample.srm"
            save_path.write_bytes(make_save())
            stdout = StringIO()
            with patch("sys.argv", ["checker", str(save_path), "--english"]):
                with redirect_stdout(stdout):
                    result = checker.main()

            self.assertEqual(result, 0)
            self.assertIn("File:", stdout.getvalue())
            self.assertIn("Chicken statue", stdout.getvalue())
            self.assertIn("Winter Flower / Blue Diamond", stdout.getvalue())
            self.assertNotIn("Estátua da galinha", stdout.getvalue())

    def test_error_messages_follow_selected_language(self) -> None:
        for flag, expected in (([], "Erro:"), (["--english"], "Error:")):
            with self.subTest(flag=flag), tempfile.TemporaryDirectory() as directory:
                save_path = Path(directory) / "too-small.srm"
                save_path.write_bytes(b"short")
                stderr = StringIO()
                with patch("sys.argv", ["checker", str(save_path), *flag]):
                    with redirect_stderr(stderr):
                        result = checker.main()
                self.assertEqual(result, 2)
                self.assertIn(expected, stderr.getvalue())

    def test_report_detects_blue_diamond_in_shed(self) -> None:
        save_data = make_valid_slot(marker=1, blue_diamond_in_shed=True) + make_valid_slot()
        with tempfile.TemporaryDirectory() as directory:
            save_path = Path(directory) / "diamond.srm"
            save_path.write_bytes(save_data)
            stdout = StringIO()
            with patch("sys.argv", ["checker", str(save_path)]):
                with redirect_stdout(stdout):
                    result = checker.main()

            self.assertEqual(result, 0)
            self.assertIn("DIAMANTE AINDA DISPONÍVEL", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
