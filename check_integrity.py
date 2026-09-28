from pathlib import Path
from tempfile import TemporaryDirectory
import json

from src.data.integrity import (calculate_sha256,
                                verify_snapshot_integrity)

with TemporaryDirectory() as temporary_directory:
    temporary_path = Path(temporary_directory)

    first_path = temporary_path / "first.csv"
    second_path = temporary_path / "second.csv"

    original_content = b"Date,Open\n2024-01-02,100.0\n"

    first_path.write_bytes(original_content)
    second_path.write_bytes(original_content)

    first_hash = calculate_sha256(first_path)
    second_hash = calculate_sha256(second_path)

    assert first_hash == second_hash, (
        "Identical bytes must produce the same SHA-256"
    )

    print("Identical content produces identical hashes.")

    metadata_path = temporary_path / "metadata.json"

    metadata = {
        "sha256": first_hash,
    }

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata,file)

    verify_snapshot_integrity(second_path,metadata_path)

    print("Matching snapshot accepted.")

    modified_content = b"Date,Open\n2024-01-02,101.0\n"

    second_path.write_bytes(modified_content)

    modified_hash = calculate_sha256(second_path)

    assert first_hash != modified_hash, (
        "Changing the content should change its SHA-256."
    )

    print("Modified content produces a different hash.")

    try:
        verify_snapshot_integrity(second_path, metadata_path)

    except ValueError as error:
        assert "Snapshot SHA-256 mismatch" in str(error), (
            f"Unexpected validation error: {error}"
        )
        print("Modified snapshot correctly rejected.")

    else:
        raise AssertionError(
            "The validator accepted a Close greater than High."
        )
