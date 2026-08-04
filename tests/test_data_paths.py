import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class DataPathTests(unittest.TestCase):
    def test_resolve_data_path_uses_project_data_folder_for_source_runs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "project"
            data_dir = project_dir / "data"
            data_dir.mkdir(parents=True)
            expected_path = data_dir / "transactions.csv"
            expected_path.write_text("amount,category,date\n", encoding="utf-8")

            with patch.object(main, "__file__", str(project_dir / "main.py")):
                with patch.object(os, "getcwd", return_value=str(project_dir)):
                    self.assertEqual(main.resolve_data_path("data/transactions.csv"), expected_path)

    def test_resolve_data_path_prefers_project_data_folder_for_new_exe_runs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "project"
            dist_dir = project_dir / "dist"
            dist_dir.mkdir(parents=True)
            expected_path = project_dir / "data" / "transactions.csv"
            expected_path.parent.mkdir(parents=True, exist_ok=True)
            expected_path.write_text("amount,category,date\n", encoding="utf-8")

            with patch.object(sys, "frozen", True, create=True):
                with patch.object(sys, "executable", str(dist_dir / "main.exe")):
                    with patch.object(os, "getcwd", return_value=str(dist_dir)):
                        self.assertEqual(main.resolve_data_path("data/transactions.csv"), expected_path)

    def test_resolve_data_path_uses_meipass_folder_for_frozen_runs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "project"
            meipass_dir = project_dir / "_MEIPASS"
            data_dir = meipass_dir / "data"
            data_dir.mkdir(parents=True)
            expected_path = data_dir / "transactions.csv"
            expected_path.write_text("amount,category,date\n", encoding="utf-8")

            with patch.object(sys, "frozen", True, create=True):
                with patch.object(sys, "executable", str(project_dir / "dist" / "main.exe")):
                    with patch.object(sys, "_MEIPASS", str(meipass_dir), create=True):
                        with patch.object(os, "getcwd", return_value=str(project_dir)):
                            self.assertEqual(main.resolve_data_path("data/transactions.csv"), expected_path)

    def test_resolve_data_path_falls_back_to_project_data_folder_for_exe_runs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "project"
            dist_dir = project_dir / "dist"
            data_dir = project_dir / "data"
            data_dir.mkdir(parents=True)
            dist_dir.mkdir(parents=True)
            expected_path = data_dir / "transactions.csv"
            expected_path.write_text("amount,category,date\n", encoding="utf-8")

            with patch.object(sys, "frozen", True, create=True):
                with patch.object(sys, "executable", str(dist_dir / "main.exe")):
                    with patch.object(os, "getcwd", return_value=str(dist_dir)):
                        self.assertEqual(main.resolve_data_path("data/transactions.csv"), expected_path)


if __name__ == "__main__":
    unittest.main()
