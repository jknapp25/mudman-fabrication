import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.classify_bambu_3mf import INVALID_CONFIG_WARNING, classify


class ClassifyBambu3mfTest(unittest.TestCase):
    def _archive(self, root, configured):
        path = root / "sample.3mf"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("3D/3dmodel.model", "<model/>")
            if configured:
                archive.writestr("Metadata/model_settings.config", "<config/>")
                archive.writestr("Metadata/project_settings.config", "{}")
        return path

    def test_geometry_cannot_claim_configured(self):
        with tempfile.TemporaryDirectory() as directory:
            result = classify(self._archive(Path(directory), False), "configured")
        self.assertEqual(result["classification"], "GEOMETRY_3MF")
        self.assertEqual(result["status"], "FAILED")

    def test_exact_warning_fails_configured_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = self._archive(root, True)
            evidence = root / "result.json"
            evidence.write_text(json.dumps({"warning_message": INVALID_CONFIG_WARNING}))
            result = classify(artifact, "configured", evidence)
        self.assertTrue(result["invalid_config_warning_detected"])
        self.assertEqual(result["status"], "FAILED")

    def test_clean_slice_can_validate_print_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = self._archive(root, True)
            evidence = root / "result.json"
            evidence.write_text(json.dumps({
                "return_code": 0,
                "sliced_plates": [{"warning_message": ""}],
            }))
            result = classify(artifact, "validated-print-ready", evidence)
        self.assertEqual(result["classification"], "VALIDATED_PRINT_READY_BAMBU_3MF")
        self.assertEqual(result["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
