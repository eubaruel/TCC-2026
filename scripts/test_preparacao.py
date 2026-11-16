"""Testa a verificacao de dependencias sem executar pip ou instalar ferramentas."""
import hashlib
import importlib.metadata
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch


LAUNCHER = Path(__file__).resolve().parents[1] / "INICIAR.cmd"
namespace = {"__file__": str(LAUNCHER), "__name__": "tcc_launcher_test"}
exec(compile(LAUNCHER.read_text(encoding="utf-8").split("\n", 1)[1], str(LAUNCHER), "exec"), namespace)
python_venv = namespace["python_venv"]


class PreparacaoTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("TCC_TEST_TEMP"))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.requirements = self.root / "requirements.txt"
        self.marker = self.root / ".tcc-requisitos.sha256"
        self.calls = []
        self.patch = patch.dict(namespace, {
            "BACKEND": self.root,
            "python_venv": lambda _: Path(sys.executable),
            "executar": lambda command, cwd: self.calls.append(command),
        })
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def write_requirements(self, text, encoding="utf-8", mark=True):
        self.requirements.write_text(text, encoding=encoding)
        if mark:
            self.marker.write_text(hashlib.sha256(self.requirements.read_bytes()).hexdigest())

    def prepare(self):
        return namespace["preparar_python"](self.root, self.requirements)

    def test_installed_requirements_reused_in_both_encodings(self):
        requirement = "Flask==" + importlib.metadata.version("Flask")
        for encoding in ("utf-8", "utf-16"):
            with self.subTest(encoding=encoding):
                self.write_requirements(requirement, encoding)
                self.prepare()
                self.assertEqual(self.calls, [])

    def test_missing_package_reinstalled_despite_existing_marker(self):
        self.write_requirements("tcc-package-deliberately-missing==1.0")
        self.prepare()
        self.assertEqual(self.calls[0][1:5], ["-m", "pip", "install", "-r"])
        self.assertEqual(self.calls[1][1:], ["-m", "pip", "check"])

    def test_first_run_installs_and_marks_requirements(self):
        self.write_requirements("Flask==3.1.3", mark=False)
        self.prepare()
        self.assertEqual(len(self.calls), 2)
        self.assertTrue(self.marker.is_file())

    def test_install_failure_does_not_mark_success(self):
        self.write_requirements("Flask==3.1.3", mark=False)
        with patch.dict(namespace, {"executar": lambda *_: (_ for _ in ()).throw(subprocess.CalledProcessError(1, "pip"))}):
            with self.assertRaises(subprocess.CalledProcessError):
                self.prepare()
        self.assertFalse(self.marker.exists())

    def test_linux_venv_path(self):
        with patch.dict(namespace, {"os": SimpleNamespace(name="posix")}):
            self.assertEqual(python_venv(self.root), self.root / "bin" / "python")

    def test_linux_frontend_runs_npm_without_cmd(self):
        (self.root / "node_modules").mkdir()
        (self.root / "package-lock.json").write_text("{}")
        (self.root / "package.json").write_text("{}")
        with patch.dict(namespace, {"os": SimpleNamespace(name="posix"), "FRONTEND": self.root}):
            namespace["preparar_frontend"]()
        self.assertEqual(self.calls, [["npm", "ci"]])


if __name__ == "__main__":
    unittest.main()
