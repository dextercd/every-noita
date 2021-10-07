import os
import subprocess
import pathlib
import shutil
from collections import namedtuple

from settings import username, password, depot_downloader_path


Manifest = namedtuple('Manifest', 'code')


manifest_list_content = open('manifests.txt').read()
manifest_all_lines = manifest_list_content.split('\n')
manifest_lines = [m for m in manifest_all_lines if m and '#' not in m]
manifest_parts = [m.split() for m in manifest_lines]
manifests = [Manifest(c) for _, _, _, _, _, _, _, _, _, c in manifest_parts]


for manifest in manifests:

    try:
        path = pathlib.Path('downloads/' + str(manifest.code))
        # Reserve directory for this instance
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(path, 'already downloaded')
        continue

    try:
        subprocess.run([
            'dotnet', depot_downloader_path,
                '-username', username,
                '-password', password,
                '-app', str(881100),
                '-depot', str(881101),
                '-manifest', str(manifest.code),
                '-dir', path],
            check=True)
    except:
        # Error, clear path for retry
        print('Download failed, removing', path)
        shutil.rmtree(path)
        raise

