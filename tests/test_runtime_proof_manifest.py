import unittest

from observability.runtime_proof_manifest import RuntimeProofManifest, MANIFEST_FILE


class TestRuntimeProofManifest(unittest.TestCase):
    def test_export_writes_manifest_file(self):
        manifest = RuntimeProofManifest.export()
        self.assertIn("proof_type", manifest)
        self.assertEqual(manifest["proof_type"], "RUNTIME_PROOF_MANIFEST")
        self.assertIn("checks", manifest)
        self.assertTrue(MANIFEST_FILE.endswith("runtime_proof_manifest.json"))


if __name__ == "__main__":
    unittest.main()
