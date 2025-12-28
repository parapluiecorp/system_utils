import argparse
import hashlib
import sys
from pathlib import Path
from typing import Union


def compute_sha1(path: Path) -> str:
    """
    Compute the SHA1 hash of a file.

    Args:
        path (Path): Path to the file.

    Returns:
        str: SHA1 hash as a hexadecimal string.

    Raises:
        PermissionError: If the file cannot be accessed.
        OSError: For other OS-related errors.
    """
    sha1 = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha1.update(chunk)
    return sha1.hexdigest()


def print_file_metadata(path: Path, compute_hash: bool = False) -> None:
    """
    Print metadata of a given file.

    Args:
        path (Path): Path to the file.
        compute_hash (bool, optional): Whether to compute SHA1 hash. Defaults to False.

    Raises:
        PermissionError: If file access is denied.
        OSError: For other OS-related errors.
    """
    stat = path.stat()

    print("\n=== FILE METADATA ===")
    print(f"Full Name:         {path.resolve()}")
    print(f"Name:              {path.name}")
    print(f"Extension:         {path.suffix}")
    print(f"Size (bytes):      {stat.st_size}")
    print(f"Created:           {stat.st_ctime}")
    print(f"Last Modified:     {stat.st_mtime}")
    print(f"Last Accessed:     {stat.st_atime}")

    if compute_hash:
        try:
            print(f"SHA1 Hash:         {compute_sha1(path)}")
        except PermissionError:
            print("SHA1 Hash:         (access denied)")


def main() -> int:
    """
    Main entry point of the script. Parses arguments and prints file metadata.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(description="Display file metadata")
    parser.add_argument(
        "path",
        help="Full path to the file"
    )
    parser.add_argument(
        "--sha1",
        action="store_true",
        help="Compute SHA1 hash of the file"
    )

    args = parser.parse_args()
    path = Path(args.path)

    try:
        if not path.exists():
            print("Error: File not found.", file=sys.stderr)
            return 1

        if not path.is_file():
            print("Error: Path is not a file.", file=sys.stderr)
            return 1

        print_file_metadata(path, compute_hash=args.sha1)
        return 0

    except PermissionError:
        print("Error: Access denied.", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"OS error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

