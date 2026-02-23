import subprocess
import sys
import unittest
from pathlib import Path
import pyperclip


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Test0100CommandCases(unittest.TestCase):
    def run_command_file(self, command_file: str, *extra_args: str) -> str:
        process = subprocess.run(
            [sys.executable, "CommandRPA.py", command_file, *extra_args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )

        combined_output = (process.stdout or "") + "\n" + (process.stderr or "")

        self.assertEqual(
            process.returncode,
            0,
            msg=f"{command_file} failed with code {process.returncode}\n{combined_output}",
        )
        return combined_output

    def test_01_01_core_basic(self):
        output = self.run_command_file("tests/commands/01_core/01_01_basic.txt")
        self.assertIn("===== 01_01_basic start =====", output)
        self.assertIn("user=hal02", output)
        self.assertIn("project=RPAmaker", output)
        self.assertIn("bool-return=True", output)
        self.assertIn("===== 01_01_basic end =====", output)

    def test_01_02_core_flow(self):
        output = self.run_command_file("tests/commands/01_core/01_02_flow.txt")
        self.assertIn("===== 01_02_flow start =====", output)
        self.assertIn("test mode selected", output)
        self.assertIn("mode is not prod", output)
        self.assertIn("===== 01_02_flow end =====", output)

    def test_01_04_core_read_parent(self):
        output = self.run_command_file("tests/commands/01_core/01_04_read_parent.txt")
        self.assertIn("===== 01_04_read_parent start =====", output)
        self.assertIn("[01_03_child] start", output)
        self.assertIn("[01_03_child] child_result=ok", output)
        self.assertIn("[01_04_parent] after child, child_result=ok", output)
        self.assertIn("===== 01_04_read_parent end =====", output)

    def test_02_01_params_cli_args(self):
        output = self.run_command_file(
            "tests/commands/02_params/02_01_cli_args.txt",
            "cli_user=tester",
            "run_id=RPA-001",
        )
        self.assertIn("===== 02_01_cli_args start =====", output)
        self.assertIn("cli_user=tester", output)
        self.assertIn("run_id=RPA-001", output)
        self.assertIn("===== 02_01_cli_args end =====", output)

    def test_02_02_params_input_default(self):
        output = self.run_command_file("tests/commands/02_params/02_02_input_default.txt")
        self.assertIn("===== 02_02_input_default start =====", output)
        self.assertIn("input=from-default", output)
        self.assertIn("===== 02_02_input_default end =====", output)

    def test_03_01_reserved_clip(self):
        expected = "clip-from-test"
        try:
            pyperclip.copy(expected)
        except pyperclip.PyperclipException as e:
            self.skipTest(f"Clipboard is not available in this environment: {e}")

        output = self.run_command_file("tests/commands/03_reserved/03_01_clip.txt")
        self.assertIn("===== 03_01_clip start =====", output)
        self.assertIn(f"clip={expected}", output)
        self.assertIn("===== 03_01_clip end =====", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
