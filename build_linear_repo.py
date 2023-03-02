import os
import subprocess
from pathlib import Path
import shutil
import datetime
from zoneinfo import ZoneInfo
import textwrap

import manifest

from settings import decprg_path


unsorted_manifests = manifest.load_file('manifests.txt')
manifests = sorted(unsorted_manifests, key=lambda m: m.datetime)

project = Path('.').resolve()
repository = project / 'linear_repo'

repository.mkdir(exist_ok=True)
os.chdir(repository)

keep_paths = ['.git']
def clear_repo():
    for item in repository.iterdir():
        if item.name in keep_paths:
            continue

        if item.is_file():
            item.unlink()
        else:
            shutil.rmtree(item)

clean_paths = [".DepotDownloader"]
def clean_repo():
    for item in repository.iterdir():
        if item.name not in clean_paths:
            continue

        if item.is_file():
            item.unlink()
        else:
            shutil.rmtree(item)

has_git = (repository / '.git').exists()
if not has_git:
    subprocess.run([
        'git', 'init',
            '--initial-branch', 'main'],
        check=True)


existing_manifests_result = subprocess.run(
    ["git", "log", "--format=%s"],
    check=True,
    capture_output=True,
    encoding="utf-8"
)
existing_manifests = [
    int(line.removeprefix("Commit manifest "))
    for line in existing_manifests_result.stdout.split("\n")
    if line
]


for manifest in manifests:

    if manifest.code in existing_manifests:
        continue

    manifest_location = project / 'downloads' / str(manifest.code)
    assert manifest_location.exists()

    print('Processing path', manifest_location)

    clear_repo()
    shutil.copytree(manifest_location, repository, dirs_exist_ok=True)
    clean_repo()

    dectypes = ['v1', 'v2', 'plain']
    decsuccess = False

    wak = repository / 'data/data.wak'
    for dectype in dectypes:
        try:
            subprocess.run([
                decprg_path, dectype,
                    wak,
                    repository],
                check=True)
            decsuccess = True
        except:
            pass

    if not decsuccess:
        raise Exception('Could not decrypt')

    wak.unlink()

    print('Converting text files to unix format')
    subprocess.run([
        'find', '.', '-type', 'f',
            '!', '-path', './.git/*',
            '-regextype', 'egrep',
            '-regex', '.*\.(txt|lua|xml|csv|bat|frag|vert)',
            '-exec', 'dos2unix', '{}', '+'],
        check=True)

    print('Removing trailing spaces')
    subprocess.run([
        'find', '.', '-type', 'f',
            '!', '-path', './.git/*',
            '-regextype', 'egrep',
            '-regex', '.*\.(txt|lua|xml|csv|bat|frag|vert)',
            '-exec', 'sed', '-i', 's/\s\+$//', '{}', '+'],
        check=True)

    dt = manifest.datetime.astimezone(ZoneInfo('Europe/Helsinki'))
    commit_message = textwrap.dedent(f"""\
    Commit manifest {manifest.code}

    Published on {dt.isoformat()}
    """)

    branch = repository / '_branch.txt'
    if branch.exists():
        commit_message += '\n\n' + textwrap.dedent(f"""\
        Branch: {open(branch).read()}
        """)

    version_hash = repository / '_version_hash.txt'
    if version_hash.exists():
        commit_message += '\n\n' + textwrap.dedent(f"""\
        Version Hash: {open(version_hash).read()}
        """)

    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run([
        'git', 'commit',
            '-m', commit_message,
            '--author=Nolla Games <noita@nollagames.com>',
            '--date', dt.isoformat()],
        check=True)
