import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from google_photos.importer import scan_source


class ScanSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_scans_folder_and_retains_full_sidecar(self):
        sidecar = self.root / "Takeout" / "Google Photos" / "Album" / "PXL_001.jpg.supplemental-metadata.json"
        sidecar.parent.mkdir(parents=True)
        metadata = {
            "title": "PXL_001.jpg",
            "photoTakenTime": {"timestamp": "1720000000", "formatted": "Jul 3, 2024, 12:26:40 PM UTC"},
            "geoData": {"latitude": 47.6, "longitude": -122.3, "altitude": 15},
            "futureField": {"kept": True},
        }
        sidecar.write_text(json.dumps(metadata), encoding="utf-8")
        (sidecar.parent / "unrelated.json").write_text("{}", encoding="utf-8")

        result = scan_source(str(self.root))

        self.assertEqual(len(result["records"]), 1)
        record = result["records"][0]
        self.assertEqual(record["media_filename"], "PXL_001.jpg")
        self.assertEqual(record["latitude"], "47.6")
        self.assertEqual(json.loads(record["raw_metadata_json"])["futureField"], {"kept": True})
        self.assertEqual(result["ignored"], 1)
        self.assertEqual(result["errors"], [])

    def test_scans_takeout_zip_and_reports_invalid_json(self):
        archive_path = self.root / "takeout.zip"
        metadata = {"title": "clip.mp4", "creationTime": {"timestamp": "1720000000"}}
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("Takeout/Google Photos/clip.mp4.json", json.dumps(metadata))
            archive.writestr("Takeout/Google Photos/broken.json", "not json")

        result = scan_source(str(archive_path))

        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["media_filename"], "clip.mp4")
        self.assertEqual(len(result["errors"]), 1)

    def test_rejects_file_that_is_not_a_takeout_zip(self):
        source = self.root / "notes.txt"
        source.write_text("not an archive", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "folder or a ZIP"):
            scan_source(str(source))


if __name__ == "__main__":
    unittest.main()