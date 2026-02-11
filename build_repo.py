"""
Build script for iMeshh Blender Extension Repository.

For each extension in extensions/, creates a .zip in packages/ and generates
an index.json that Blender can read as a remote extension repository.
"""

import json
import hashlib
import os
import zipfile
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

EXTENSIONS_DIR = Path("extensions")
PACKAGES_DIR = Path("packages")


def build_extension_zip(ext_dir: Path) -> Path:
    """Zip an extension folder into packages/."""
    manifest_path = ext_dir / "blender_manifest.toml"
    with open(manifest_path, "rb") as f:
        manifest = tomllib.load(f)

    ext_id = manifest["id"]
    version = manifest["version"]
    zip_name = f"{ext_id}-{version}.zip"
    zip_path = PACKAGES_DIR / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ext_dir):
            # Skip __pycache__
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(ext_dir)
                zf.write(file_path, arcname)

    return zip_path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_index():
    """Build index.json from all extensions."""
    PACKAGES_DIR.mkdir(exist_ok=True)

    data = {
        "version": "v1",
        "blocklist": [],
        "data": [],
    }

    if not EXTENSIONS_DIR.exists():
        print("No extensions/ directory found.")
        return

    for ext_dir in sorted(EXTENSIONS_DIR.iterdir()):
        manifest_path = ext_dir / "blender_manifest.toml"
        if not manifest_path.exists():
            continue

        print(f"Building: {ext_dir.name}")

        with open(manifest_path, "rb") as f:
            manifest = tomllib.load(f)

        zip_path = build_extension_zip(ext_dir)
        file_size = zip_path.stat().st_size
        file_hash = "sha256:" + sha256_file(zip_path)

        entry = {
            "schema_version": manifest.get("schema_version", "1.0.0"),
            "id": manifest["id"],
            "name": manifest["name"],
            "version": manifest["version"],
            "tagline": manifest.get("tagline", ""),
            "maintainer": manifest.get("maintainer", ""),
            "type": manifest.get("type", "add-on"),
            "tags": manifest.get("tags", []),
            "blender_version_min": manifest.get("blender_version_min", "4.2.0"),
            "website": manifest.get("website", ""),
            "archive_url": f"./packages/{zip_path.name}",
            "archive_size": file_size,
            "archive_hash": file_hash,
        }

        if "blender_version_max" in manifest:
            entry["blender_version_max"] = manifest["blender_version_max"]
        if "license" in manifest:
            entry["license"] = manifest["license"]

        data["data"].append(entry)

    with open(PACKAGES_DIR / "index.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nBuilt {len(data['data'])} extension(s) -> packages/index.json")


if __name__ == "__main__":
    build_index()
