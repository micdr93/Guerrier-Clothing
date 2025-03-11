import os
import shutil
import pathlib


def ensure_static_files():
    directories = [
        "static/css",
        "static/js",
        "static/checkout/js",
        "static/images",
        "static/images/favicon",
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    files_to_create = {
        "static/css/base.css": "/* Base styling */",
        "static/js/scripts.js": "// Scripts",
        "static/checkout/js/stripe_elements.js": "// Stripe elements script",
        "static/images/favicon/site.webmanifest": """{
  "name": "Guerrier",
  "short_name": "Guerrier",
  "display": "standalone"
}""",
    }

    for path, content in files_to_create.items():
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(content)

    # Copy carousel images if they exist
    image_sources = ["media/images", "staticfiles/images", "media", "staticfiles"]

    for source_dir in image_sources:
        if os.path.exists(source_dir):
            for img in ["carousel1.webp", "carousel2.webp", "carousel3.webp"]:
                source_path = os.path.join(source_dir, img)
                dest_path = os.path.join("static/images", img)
                if os.path.exists(source_path) and not os.path.exists(dest_path):
                    shutil.copy(source_path, dest_path)


if __name__ == "__main__":
    ensure_static_files()
