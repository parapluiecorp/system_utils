import argparse
import hashlib
import sys
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import os
import stat
import pwd
import grp
import mimetypes

@dataclass
class FileMeta:
    """Holds metadata for a single file."""
    full_path: Path
    name: str
    stem: str
    suffix: str
    suffixes: List[str]
    parent: Path
    size_bytes: int
    created: datetime
    modified: datetime
    accessed: datetime
    mode: int
    permissions: str
    n_links: int
    owner_uid: int
    owner_name: Optional[str]
    group_gid: int
    group_name: Optional[str]
    is_file: bool
    is_dir: bool
    is_symlink: bool
    mime_type: Optional[str] = None
    sha1_hash: Optional[str] = None

def compute_sha1(path: Path) -> str:
    """Compute SHA1 hash of a file."""
    sha1 = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha1.update(chunk)
    return sha1.hexdigest()

def get_file_metadata(path: Path, compute_hash: bool = False) -> FileMeta:
    """
    Collect all available metadata for a file into a FileMeta object.

    Args:
        path (Path): Path to the file.
        compute_hash (bool, optional): Whether to compute SHA1 hash. Defaults to False.

    Returns:
        FileMeta: Object containing all file metadata.
    """
    stat_info = path.stat()
    
    # Owner and group names (Unix)
    try:
        owner_name = pwd.getpwuid(stat_info.st_uid).pw_name
    except KeyError:
        owner_name = None
    try:
        group_name = grp.getgrgid(stat_info.st_gid).gr_name
    except KeyError:
        group_name = None
    
    mime_type, _ = mimetypes.guess_type(str(path))
    
    sha1 = None
    if compute_hash:
        try:
            sha1 = compute_sha1(path)
        except PermissionError:
            sha1 = "(access denied)"

    return FileMeta(
        full_path=path.resolve(),
        name=path.name,
        stem=path.stem,
        suffix=path.suffix,
        suffixes=path.suffixes,
        parent=path.parent,
        size_bytes=stat_info.st_size,
        created=datetime.fromtimestamp(stat_info.st_ctime),
        modified=datetime.fromtimestamp(stat_info.st_mtime),
        accessed=datetime.fromtimestamp(stat_info.st_atime),
        mode=stat_info.st_mode,
        permissions=oct(stat_info.st_mode & 0o777),
        n_links=stat_info.st_nlink,
        owner_uid=stat_info.st_uid,
        owner_name=owner_name,
        group_gid=stat_info.st_gid,
        group_name=group_name,
        is_file=path.is_file(),
        is_dir=path.is_dir(),
        is_symlink=path.is_symlink(),
        mime_type=mime_type,
        sha1_hash=sha1
    )

def print_file_metadata(meta: FileMeta) -> None:
    """Print all metadata stored in a FileMeta object."""
    print("\n=== FILE METADATA ===")
    print(f"Full Path:         {meta.full_path}")
    print(f"Name:              {meta.name}")
    print(f"Stem:              {meta.stem}")
    print(f"Extension:         {meta.suffix}")
    print(f"All Extensions:    {meta.suffixes}")
    print(f"Parent Directory:  {meta.parent}")
    print(f"Size (bytes):      {meta.size_bytes}")
    print(f"Created:           {meta.created}")
    print(f"Last Modified:     {meta.modified}")
    print(f"Last Accessed:     {meta.accessed}")
    print(f"Mode:              {meta.mode} ({meta.permissions})")
    print(f"Number of Links:   {meta.n_links}")
    print(f"Owner UID/Name:    {meta.owner_uid} / {meta.owner_name}")
    print(f"Group GID/Name:    {meta.group_gid} / {meta.group_name}")
    print(f"Is File:           {meta.is_file}")
    print(f"Is Directory:      {meta.is_dir}")
    print(f"Is Symlink:        {meta.is_symlink}")
    print(f"MIME Type:         {meta.mime_type}")
    if meta.sha1_hash is not None:
        print(f"SHA1 Hash:         {meta.sha1_hash}")

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Display file metadata")
    parser.add_argument("path", help="Full path to the file")
    parser.add_argument("--sha1", action="store_true", help="Compute SHA1 hash")
    args = parser.parse_args()

    path = Path(args.path)

    try:
        if not path.exists():
            print("Error: File not found.", file=sys.stderr)
            return 1
        if not path.is_file():
            print("Error: Path is not a file.", file=sys.stderr)
            return 1

        meta = get_file_metadata(path, compute_hash=args.sha1)
        print_file_metadata(meta)

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

