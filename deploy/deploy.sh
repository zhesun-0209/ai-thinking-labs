#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd -- "$HERE/.." && pwd)
fail() { printf 'Error: %s\n' "$*" >&2; exit 1; }
usage() {
    cat <<'HELP'
Local build (no network):
  bash deploy/deploy.sh build --site-url https://DOMAIN --output NEW_DIRECTORY
Deploy an inspected package (dry run unless --execute is supplied):
  bash deploy/deploy.sh deploy --package DIRECTORY --host HOST --user USER \
    --known-hosts FILE [--identity FILE] [--port 22] [--execute]
Rollback to a retained release (also dry run by default):
  bash deploy/deploy.sh rollback --release RELEASE_ID --site-url https://DOMAIN \
    --host HOST --user USER --known-hosts FILE [--identity FILE] [--port 22] \
    [--remote-root /srv/ai-thinking-labs] [--execute]
Server provisioning, Caddy installation/configuration and DNS are manual prerequisites.
HELP
}

action=${1:-help}
[[ $# == 0 ]] || shift
case "$action" in
    help|--help|-h) usage; exit 0 ;;
    build) exec python3 "$REPO/scripts/build_site.py" "$@" ;;
    deploy|rollback) ;;
    *) usage; fail "unknown action: $action" ;;
esac

host= user= known_hosts= identity= package= release= site_url=
remote_root=/srv/ai-thinking-labs
port=22
execute=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --execute) execute=true; shift; continue ;;
        --help|-h) usage; exit 0 ;;
    esac
    [[ $# -ge 2 ]] || fail "missing value for $1"
    case "$1" in
        --host) host=$2 ;;
        --user) user=$2 ;;
        --known-hosts) known_hosts=$2 ;;
        --identity) identity=$2 ;;
        --package) package=$2 ;;
        --release) release=$2 ;;
        --site-url) site_url=$2 ;;
        --remote-root) remote_root=$2 ;;
        --port) port=$2 ;;
        *) fail "unknown option: $1" ;;
    esac
    shift 2
done

[[ "$host" =~ ^[A-Za-z0-9][A-Za-z0-9.-]*$ ]] || fail "set --host to an SSH DNS name or IPv4 address"
[[ "$user" =~ ^[a-z_][a-z0-9_-]*$ && "$user" != root ]] || fail "use a non-root deployment user"
[[ "$port" =~ ^[1-9][0-9]{0,4}$ ]] && ((port <= 65535)) || fail "invalid SSH port"
[[ -f "$known_hosts" && -s "$known_hosts" ]] || fail "provide an independently verified, nonempty known_hosts file"

if [[ "$action" == deploy ]]; then
    [[ -d "$package" ]] || fail "provide --package from the local build"
    metadata=$(python3 -I - "$REPO/scripts/build_site.py" "$package" <<'PY'
import hashlib, json, pathlib, runpy, sys
builder = runpy.run_path(sys.argv[1])
package = pathlib.Path(sys.argv[2]).resolve()
report = json.loads((package / 'build-report.json').read_text())
assert report['format'] == 1 and report['deployment_ready'], 'package must target a domain root'
url = builder['normalize_site_url'](report['site_url'])
assert url == report['site_url'] and url.count('/') == 3, 'root URL required'
root = builder['validate_remote_root'](report['remote_root'])
digest = hashlib.sha256((package / 'site.tar.gz').read_bytes()).hexdigest()
assert digest == report['archive_sha256'], 'archive checksum mismatch'
print(url, root, digest, sep='\t')
PY
    )
    IFS=$'\t' read -r site_url remote_root digest <<< "$metadata"
    release="$(date -u +%Y%m%dT%H%M%SZ)-$(python3 -c 'import secrets; print(secrets.token_hex(4))')"
else
    [[ "$release" =~ ^[0-9]{8}T[0-9]{6}Z-[a-f0-9]{8}$ ]] || fail "invalid release ID"
    digest=-
fi

metadata=$(python3 -I - "$REPO/scripts/build_site.py" "$site_url" "$remote_root" <<'PY'
import runpy, sys
b = runpy.run_path(sys.argv[1])
url = b['normalize_site_url'](sys.argv[2])
assert url.count('/') == 3, 'deployment requires a domain-root URL'
root = b['validate_remote_root'](sys.argv[3])
print(url, root, sep='\t')
PY
)
IFS=$'\t' read -r site_url remote_root <<< "$metadata"
domain=${site_url#https://}
domain=${domain%/}
target="$user@$host"
known_hosts=$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve())' "$known_hosts")
ssh_options=(-F /dev/null -o "Port=$port" -o BatchMode=yes -o StrictHostKeyChecking=yes
    -o "UserKnownHostsFile=$known_hosts" -o GlobalKnownHostsFile=/dev/null
    -o UpdateHostKeys=no -o ForwardAgent=no -o ClearAllForwardings=yes -o ConnectTimeout=10)
if [[ -n "$identity" ]]; then
    [[ -f "$identity" ]] || fail "identity file does not exist"
    identity=$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve())' "$identity")
    case "$identity" in "$REPO"/*) fail "SSH private keys must stay outside the repository" ;; esac
    ssh_options+=(-o IdentitiesOnly=yes -i "$identity")
fi

printf '%s release %s -> %s:%s (%s)\n' "$action" "$release" "$target" "$remote_root" "$site_url"
if [[ "$execute" != true ]]; then
    printf 'Dry run only: no SSH/SCP was run. Review docs/migration-tencent.md before adding --execute.\n'
    exit 0
fi

upload="$remote_root/incoming/$release"
if [[ "$action" == deploy ]]; then
    ssh "${ssh_options[@]}" "$target" "umask 077; test -d '$remote_root/releases' && mkdir '$upload'"
    cleanup_upload() {
        ssh "${ssh_options[@]}" "$target" "rm -f '$upload/site.tar.gz' '$upload/build-report.json'; rmdir '$upload'" || true
    }
    trap cleanup_upload EXIT
    scp "${ssh_options[@]}" "$package/site.tar.gz" "$package/build-report.json" "$target:$upload/"
fi

ssh "${ssh_options[@]}" "$target" "bash -s -- '$action' '$remote_root' '$release' '$site_url' '$digest'" <<'REMOTE'
set -euo pipefail
action=$1 root=$2 release=$3 site_url=$4 digest=$5
[[ $(id -u) != 0 ]] || { echo 'Refusing root deployment' >&2; exit 1; }
[[ -d "$root/releases" && -d "$root/incoming" && ! -L "$root/releases" ]] || exit 1
exec 9>"$root/.deploy.lock"
flock -n 9 || { echo 'Another deployment is active' >&2; exit 1; }
umask 022
destination="$root/releases/$release"
stage="$root/releases/.staging-$release"
old=
if [[ -L "$root/current" ]]; then
    old=$(readlink "$root/current")
    [[ "$old" =~ ^releases/[0-9]{8}T[0-9]{6}Z-[a-f0-9]{8}/public$ && -d "$root/$old" ]] || exit 1
elif [[ -e "$root/current" ]]; then
    echo 'current must be a symlink, not a directory' >&2
    exit 1
fi
pending=false
finish() {
    result=$?
    trap - EXIT HUP INT TERM
    if [[ "$pending" == true ]]; then
        if [[ -n "$old" ]]; then
            ln -s "$old" "$root/.restore-$release"
            mv -Tf "$root/.restore-$release" "$root/current"
        else
            rm -f "$root/current"
        fi
        echo 'Activation failed; restored the previous current pointer.' >&2
    fi
    rm -f "$root/.current-$release" "$root/.previous-$release"
    [[ ! -d "$stage" ]] || rm -rf -- "$stage"
    exit "$result"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' HUP TERM

if [[ "$action" == deploy ]]; then
    [[ ! -e "$destination" && ! -e "$stage" ]] || exit 1
    mkdir "$stage"
    python3 -I - "$root/incoming/$release" "$stage" "$digest" "$site_url" <<'PY'
import hashlib, json, pathlib, shutil, sys, tarfile
incoming, stage = map(pathlib.Path, sys.argv[1:3])
archive = incoming / 'site.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == sys.argv[3], 'archive checksum mismatch'
report = json.loads((incoming / 'build-report.json').read_text())
assert report['site_url'] == sys.argv[4] and report['archive_sha256'] == sys.argv[3]
files = report['files']
public = stage / 'public'
public.mkdir(mode=0o755)
with tarfile.open(archive, 'r:gz') as tar:
    members = tar.getmembers()
    assert len(members) == len(files) and {m.name for m in members} == set(files), 'archive file set mismatch'
    for member in members:
        path = pathlib.PurePosixPath(member.name)
        assert member.isfile() and not path.is_absolute() and '..' not in path.parts
        assert str(path) == member.name and not any(p.startswith('.') for p in path.parts)
        expected = files[member.name]
        assert member.size == expected['bytes']
        data = tar.extractfile(member).read()
        assert hashlib.sha256(data).hexdigest() == expected['sha256'], 'public file checksum mismatch'
        dest = public / member.name
        dest.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
        dest.write_bytes(data)
        dest.chmod(0o644)
shutil.copyfile(incoming / 'build-report.json', stage / 'build-report.json')
PY
    mv -- "$stage" "$destination"
fi

# Rollback also verifies the retained release; reports are never served publicly.
python3 -I - "$destination" "$site_url" <<'PY'
import hashlib, json, pathlib, sys
release = pathlib.Path(sys.argv[1])
assert not release.is_symlink() and not (release / 'public').is_symlink()
report = json.loads((release / 'build-report.json').read_text())
assert report['site_url'] == sys.argv[2], 'release belongs to a different site URL'
actual = {p.relative_to(release / 'public').as_posix() for p in (release / 'public').rglob('*') if p.is_file()}
assert actual == set(report['files']), 'release file set changed'
assert not any(p.is_symlink() for p in (release / 'public').rglob('*'))
for name, item in report['files'].items():
    assert hashlib.sha256((release / 'public' / name).read_bytes()).hexdigest() == item['sha256']
PY
ln -s "releases/$release/public" "$root/.current-$release"
pending=true
mv -Tf "$root/.current-$release" "$root/current"
domain=${site_url#https://}
domain=${domain%/}
health=$(mktemp)
for page in hub.html notebooks/ch05_campus_search.ipynb; do
    if ! curl --noproxy '*' --fail --silent --show-error --max-time 15 --retry 4 --retry-delay 2 \
        --resolve "$domain:443:127.0.0.1" "$site_url$page" -o "$health" \
        || ! cmp -s "$health" "$destination/public/$page"; then
        rm -f "$health"
        exit 1
    fi
done
rm -f "$health"
if [[ -n "$old" ]]; then
    ln -s "$old" "$root/.previous-$release"
    mv -Tf "$root/.previous-$release" "$root/previous"
fi
pending=false
printf 'Active release: %s\nPrevious target: %s\n' "$release" "${old:-none}"
REMOTE
