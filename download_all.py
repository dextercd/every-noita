import os
import subprocess
import pathlib
import shutil

import manifest

from settings import username, password, depot_downloader_path


download_count = 0

manifests = manifest.load_file('manifests.txt')
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

        download_count += 1
        if download_count % 20 == 0:
            print('Running rdfind')
            subprocess.run([
                'rdfind',
                    '-makehardlinks', 'true',
                    'downloads/'],
                check=True)
    except:
        # Error, clear path for retry
        print('Download failed, removing', path)
        shutil.rmtree(path)
        raise

