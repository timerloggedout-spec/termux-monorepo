import unittest
from scripts.localization.validate import validate

class LocalizationContractTests(unittest.TestCase):
    def test_registry_catalog_mapping_and_manifest_are_consistent(self):
        self.assertEqual(validate(), [])

if __name__ == "__main__":
    unittest.main()
