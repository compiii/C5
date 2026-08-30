"""Write supplied exercise files without absolute paths, traversal or symlinks."""
import os
import stat
from pathlib import PurePosixPath


def write_inputs(home, entries):
    if not isinstance(entries, list) or len(entries) > 100:
        raise ValueError("Invalid input file list")
    for name, content in entries:
        parts = PurePosixPath(name).parts
        if (not parts or name.startswith('/') or '\\' in name or parts[0] in {'a.out', 'target'} or
                any(p in ('.', '..') for p in name.split('/')) or len(parts) > 16 or
                not isinstance(content, str) or len(content.encode('utf8')) > 1048576):
            raise ValueError("Invalid input file")
        fd = os.open(home, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for part in parts[:-1]:
                try:
                    os.mkdir(part, 0o770, dir_fd=fd)
                except FileExistsError:
                    pass
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = child
            # Validate the opened inode before truncating, including repeated runs.
            out = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_NONBLOCK | os.O_NOFOLLOW,
                          0o660, dir_fd=fd)
            with os.fdopen(out, 'w', encoding='utf8') as stream:
                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ValueError('Input must be a regular unlinked file')
                os.ftruncate(stream.fileno(), 0)
                stream.write(content)
        finally:
            os.close(fd)
