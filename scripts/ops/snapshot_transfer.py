"""Copy standalone snapshot files; database validation stays in core restore."""
import hashlib
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile


def open_snapshot(path):
    for suffix in ("-wal", "-shm", "-journal"):
        if os.path.lexists(str(path) + suffix):
            raise ValueError(f"Snapshot has a companion file: {path}{suffix}")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    stream = os.fdopen(descriptor, "rb")
    info = os.fstat(stream.fileno())
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        stream.close()
        raise ValueError(f"Snapshot must be a regular, single-link file: {path}")
    return stream


def main():
    action, *args = sys.argv[1:]
    if action == "describe":
        with open_snapshot(Path(args[0])) as source:
            size = os.fstat(source.fileno()).st_size
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        print(size, digest)
        return

    # Imported only in the application image, not by the host metadata step.
    from ipam_demo.store import exclusive_data_access

    data = Path(os.environ.get("IPAM_DATA_DIR", "/data"))
    with exclusive_data_access(data):
        directory = data / "snapshots"
        if directory.is_symlink():
            raise ValueError("Snapshot directory must not be a symlink")
        directory.mkdir(mode=0o700, exist_ok=True)
        if action == "list":
            for entry in sorted(directory.iterdir()):
                print(entry.name)
            return
        name = args[0]
        if not name or name in (".", "..") or "/" in name:
            raise ValueError("Snapshot must be a plain filename")
        path = directory / name
        if action == "export":
            with open_snapshot(path) as source:
                shutil.copyfileobj(source, sys.stdout.buffer)
        elif action == "import":
            expected_size, expected_hash = int(args[1]), args[2]
            if os.path.lexists(path):
                raise FileExistsError(f"Snapshot already exists: {path}")
            for suffix in ("-wal", "-shm", "-journal"):
                if os.path.lexists(str(path) + suffix):
                    raise ValueError("Destination has a companion file")
            descriptor, temporary = tempfile.mkstemp(prefix=".import-", dir=directory)
            try:
                with os.fdopen(descriptor, "wb") as destination:
                    digest = hashlib.sha256()
                    received = 0
                    while chunk := sys.stdin.buffer.read(1024 * 1024):
                        received += len(chunk)
                        if received > expected_size:
                            raise ValueError("Import exceeds source size")
                        digest.update(chunk)
                        destination.write(chunk)
                    if received != expected_size or digest.hexdigest() != expected_hash:
                        raise ValueError("Incomplete or changed snapshot transfer; not published")
                    destination.flush()
                    os.fsync(destination.fileno())
                os.link(temporary, path)  # Atomic publication; never overwrite.
            finally:
                os.unlink(temporary)
        elif action == "remove":
            with open_snapshot(path):
                path.unlink()
        else:
            raise ValueError(f"Unknown action: {action}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Snapshot transfer failed: {error}", file=sys.stderr)
        sys.exit(1)
