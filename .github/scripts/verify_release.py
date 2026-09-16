"""Transport existing audited distributions. Never build packages."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

REPOSITORY = 'cheerstopriya/authdrift'
SOURCE = 'e1442cc694eaf0a9a75c689d16a7ae52e0813d9e'
TAG = 'v0.1.0'
EXPECTED = {
    'authdrift_harness-0.1.0-py3-none-any.whl':
        '77c9cdded7eed1bf598b4f5bdb564603464401568b504347c53a7d4c0c80f9e2',
    'authdrift_harness-0.1.0.tar.gz':
        '2ccc44be242b59db77213c1a5f6e0b654f9d2167c0806cb676159aa819793fc6',
}

def api(path, *, binary=False):
    command = ['gh', 'api', '--hostname', 'github.com',
               f'repos/{REPOSITORY}/{path}', '-H',
               'Accept: application/octet-stream' if binary else
               'Accept: application/vnd.github+json']
    response = subprocess.run(command, check=True, capture_output=True).stdout
    return response if binary else json.loads(response)

def verify_tag():
    obj = api(f'git/ref/tags/{TAG}')['object']
    for _ in range(5):
        if obj['type'] == 'commit':
            if obj['sha'] != SOURCE:
                raise ValueError('Release tag does not resolve to approved source')
            print(f'{TAG} -> {SOURCE}: PASS', flush=True)
            return
        if obj['type'] != 'tag':
            break
        obj = api(f"git/tags/{obj['sha']}")['object']
    raise ValueError('Invalid release tag')

def verify_files(directory):
    entries = list(directory.iterdir())
    if (len(entries) != 2 or {p.name for p in entries} != set(EXPECTED)
            or any(p.is_symlink() or not p.is_file() for p in entries)):
        raise ValueError('Expected exactly the two approved regular distribution files')
    for name, expected in EXPECTED.items():
        actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        print(f'{name}\nexpected SHA256: {expected}\nactual SHA256:   {actual}', flush=True)
        if actual != expected:
            raise ValueError(f'SHA256 mismatch: {name}')
        print('MATCH: YES', flush=True)

def selected_assets(release):
    if release.get('tag_name') != TAG:
        raise ValueError('Selected release is not v0.1.0')
    assets = release.get('assets', [])
    if len(assets) != 2 or {a['name'] for a in assets} != set(EXPECTED):
        raise ValueError('Release must contain exactly two assets with approved names')
    if any(a.get('state') != 'uploaded' or type(a.get('id')) is not int for a in assets):
        raise ValueError('Incomplete or invalid release assets')
    return assets

def fetch(directory):
    release_id = os.environ.get('RELEASE_ID', '')
    if not re.fullmatch(r'[1-9][0-9]*', release_id):
        raise ValueError('Explicit numeric release ID required')
    verify_tag()
    release = api(f'releases/{release_id}')
    if release.get('id') != int(release_id):
        raise ValueError('Release ID mismatch')
    assets = selected_assets(release)
    directory.mkdir(exist_ok=True)
    if list(directory.iterdir()):
        raise ValueError('Artifact destination must be empty')
    print(f'Artifact source: {REPOSITORY}, release ID {release_id}', flush=True)
    for asset in assets:
        print(f"Downloading asset ID {asset['id']}: {asset['name']}", flush=True)
        (directory / asset['name']).write_bytes(api(f"releases/assets/{asset['id']}", binary=True))
    verify_files(directory)

if __name__ == '__main__':
    try:
        mode, destination = sys.argv[1:]
        directory = Path(destination)
        if mode == 'fetch':
            fetch(directory)
        elif mode == 'prepublish':
            verify_files(directory)
            verify_tag()
        elif mode == 'local':
            verify_files(directory)
        else:
            raise ValueError('Unsupported verification mode')
    except Exception as exc:
        print(f'VERIFICATION FAILED: {type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
