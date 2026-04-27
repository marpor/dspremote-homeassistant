"""Build dspremote-ha.zip for HACS (run from dspremote-homeassistant repo root)."""

from __future__ import annotations

from pathlib import Path
import zipfile


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    integration_root = repo_root / "custom_components" / "dspremote"
    output_dir = repo_root / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "dspremote-ha.zip"

    if not integration_root.is_dir():
        raise FileNotFoundError(f"integration folder not found: {integration_root}")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(integration_root.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(integration_root)
            archive_name = Path("custom_components") / "dspremote" / rel
            archive.write(path, archive_name.as_posix())

    print(f"built {zip_path}")


if __name__ == "__main__":
    main()
