import os

TAR_EXTENSION = '.tar.gz'
ZIP_EXTENSION = '.zip'

ALLOWED_EXTENSIONS = (TAR_EXTENSION,
                      ZIP_EXTENSION,
                      )

def archive_extension(filename):
    for extension in ALLOWED_EXTENSIONS:
        if extension in filename:
            return extension

def decompress_archives(path):
    archives = os.listdir(path)

    for archive in archives:
        ext = archive_extension(archive)
        if not ext:
            continue

        full_path = os.path.join(path, archive)

        basename = archive.split(ext)[0]
        new_dir = os.path.join(path, basename)

        if os.path.exists(new_dir):
            print('{} already exists! Continuing...'.format(new_dir))
            continue

        os.mkdir(new_dir)
        os.rename(full_path, os.path.join(new_dir, archive))
