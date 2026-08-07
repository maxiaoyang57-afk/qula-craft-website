import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops


SCRIPT = Path(__file__).parents[1] / "pdp_image_batch.py"


class PdpImageBatchTest(unittest.TestCase):
    def test_replaces_only_requested_sku_with_three_webp_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site = root / "site"
            source = root / "source"
            output = root / "output"
            backup = root / "backup"
            image_dir = site / "assets/images/pdp/test1"
            data_dir = site / "assets/data"
            image_dir.mkdir(parents=True)
            data_dir.mkdir(parents=True)
            source.mkdir()

            for index, color in enumerate(("red", "green", "blue"), 1):
                Image.new("RGB", (640 + index, 500 + index), color).save(
                    source / f"source-{index}.jpg"
                )
            for index in range(1, 5):
                Image.new("RGB", (800, 800), "gray").save(
                    image_dir / f"{index:02}.webp", "WEBP"
                )

            (data_dir / "pdp-data.json").write_text(
                json.dumps(
                    [
                        {
                            "sku": "TEST1",
                            "assetKey": "test1",
                            "imagesLocal": [
                                f"assets/images/pdp/test1/{index:02}.webp"
                                for index in range(1, 5)
                            ],
                        },
                        {
                            "sku": "UNCHANGED",
                            "assetKey": "unchanged",
                            "imagesLocal": ["keep.webp"],
                        },
                    ],
                    indent=2,
                ),
                encoding="utf-8",
            )
            product_schema = {
                "@context": "https://schema.org",
                "@type": "Product",
                "sku": "TEST1",
                "image": [
                    f"https://www.qulacrafts.com/assets/images/pdp/test1/{index:02}.webp"
                    for index in range(1, 5)
                ],
            }
            (site / "p-test1.html").write_text(
                "<html><head>"
                '<link rel="stylesheet" href="assets/css/ux.css">'
                '<script type="application/ld+json">'
                + json.dumps(product_schema)
                + "</script></head><body>"
                '<div class="gallery-main"><img src="assets/images/pdp/test1/01.webp"></div>'
                '<div class="gallery-row">'
                '<img src="assets/images/pdp/test1/02.webp">'
                '<img src="assets/images/pdp/test1/03.webp">'
                '<img src="assets/images/pdp/test1/04.webp">'
                "</div></body></html>",
                encoding="utf-8",
            )
            job = root / "job.json"
            job.write_text(
                json.dumps(
                    {
                        "source_root": str(source),
                        "output_root": str(output),
                        "backup_root": str(backup),
                        "items": [
                            {
                                "sku": "TEST1",
                                "files": [
                                    "source-1.jpg",
                                    "source-2.jpg",
                                    "source-3.jpg",
                                ],
                                "alts": ["hand view", "loose view", "pack view"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--site", str(site), "--job", str(job)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            data = json.loads((data_dir / "pdp-data.json").read_text(encoding="utf-8"))
            self.assertEqual(len(data[0]["imagesLocal"]), 3)
            self.assertEqual(data[1]["imagesLocal"], ["keep.webp"])

            html = (site / "p-test1.html").read_text(encoding="utf-8")
            self.assertNotIn("/04.webp", html)
            self.assertEqual(html.count('class="gallery-row"'), 1)
            self.assertEqual(html.count("assets/images/pdp/test1/01.webp"), 3)
            self.assertIn("table-layout:fixed", html)

            for index in range(1, 4):
                with Image.open(image_dir / f"{index:02}.webp") as image:
                    self.assertEqual(image.size, (1200, 1200))
                    if index == 1:
                        diff = ImageChops.difference(
                            image.convert("RGB"), Image.new("RGB", image.size, "white")
                        )
                        bbox = diff.getbbox()
                        self.assertIsNotNone(bbox)
                        self.assertEqual(max(bbox[2] - bbox[0], bbox[3] - bbox[1]), 1200)
            self.assertEqual(len(list(output.rglob("*.webp"))), 3)
            self.assertEqual(len(list(backup.rglob("*.webp"))), 4)
            self.assertTrue((output / "image-manifest.csv").exists())


if __name__ == "__main__":
    unittest.main()
