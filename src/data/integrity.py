import hashlib
from pathlib import Path
import json

def calculate_sha256(path: Path) -> str:
    """Calcula la huella SHA-256 de los bytes de un archivo."""

    with path.open("rb") as file:
        digest = hashlib.file_digest(file, "sha256")

    return digest.hexdigest()

def verify_snapshot_integrity(
    snapshot_path: Path,
    metadata_path: Path,
) -> None:
    """Comprueba que el CSV coincide con la huella de sus metadatos."""

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    expected_sha256 = metadata["sha256"]
    actual_sha256 = calculate_sha256(snapshot_path)

    if actual_sha256 != expected_sha256:
        raise ValueError(
            "Snapshot SHA-256 mismatch. "
            f"Expected: {expected_sha256}. "
            f"Actual: {actual_sha256}."
        )
    print("Snapshot SHA-256 check passed.")