import os
import shutil
from pathlib import Path


def ensure_directories(directories):
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def create_files(files_to_create):
    for path, content in files_to_create.items():
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(content)


def copy_images(image_sources, images, dest_dir):
    for source_dir in image_sources:
        if os.path.exists(source_dir):
            for img in images:
                source_path = os.path.join(source_dir, img)
                dest_path = os.path.join(dest_dir, img)
        if os.path.exists(source_path):
            and not os.path.exists(dest_path):
            shutil.copy(source_path, dest_path)


def ensure_static_files():
    directories = [
        "static/css",
        "static/js",
        "static/checkout/js",
        "static/images",
        "static/images/favicon",
    ]
    ensure_directories(directories)

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
    create_files(files_to_create)

    image_sources = [
    "media/images", "staticfiles/images",
    "media", "staticfiles"
    ]
    images = ["carousel1.webp", "carousel2.webp", "carousel3.webp"]
    copy_images(image_sources, images, "static/images")


if __name__ == "__main__":
    ensure_static_files()