#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
pin="$repo_root/runtime/bambu-studio.json"
runtime_dir=${MUDMAN_BAMBU_RUNTIME_DIR:-/tmp/mudman-bambu-studio}

read_pin() {
  python3 - "$pin" "$1" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))[sys.argv[2]]
if isinstance(value, list):
    print("\n".join(value))
else:
    print(value)
PY
}

expected_arch=x86_64
[[ $(uname -m) == "$expected_arch" ]] || { echo "Unsupported architecture: $(uname -m)" >&2; exit 2; }
[[ -r /etc/os-release ]] || { echo "Missing /etc/os-release" >&2; exit 2; }
. /etc/os-release
[[ ${ID:-} == ubuntu && ${VERSION_ID:-} == 24.04 ]] || {
  echo "Pinned runtime supports Ubuntu 24.04 x86-64; found ${ID:-unknown} ${VERSION_ID:-unknown}" >&2
  exit 2
}

mkdir -p "$runtime_dir/download" "$runtime_dir/app" "$runtime_dir/deps" \
  "$runtime_dir/apt/etc" "$runtime_dir/apt/state/lists/partial" \
  "$runtime_dir/apt/cache/archives/partial"
appimage="$runtime_dir/download/BambuStudio.AppImage"
url=$(read_pin url)
expected_sha=$(read_pin sha256)

if [[ ! -f $appimage ]] || [[ $(sha256sum "$appimage" | awk '{print $1}') != "$expected_sha" ]]; then
  curl -L --fail --retry 3 -o "$appimage" "$url"
fi
actual_sha=$(sha256sum "$appimage" | awk '{print $1}')
[[ $actual_sha == "$expected_sha" ]] || { echo "Bambu AppImage checksum mismatch" >&2; exit 3; }
chmod +x "$appimage"

if [[ ! -x $runtime_dir/app/bin/bambu-studio ]]; then
  stage=$(mktemp -d "$runtime_dir/extract.XXXXXX")
  (cd "$stage" && "$appimage" --appimage-extract >/dev/null)
  mv "$stage/squashfs-root"/* "$runtime_dir/app/"
  rmdir "$stage/squashfs-root" "$stage"
fi

if [[ ! -x $runtime_dir/deps/usr/bin/Xvfb ]] || \
  env LD_LIBRARY_PATH="$runtime_dir/app/bin:$runtime_dir/deps/usr/lib/x86_64-linux-gnu" \
    ldd "$runtime_dir/app/bin/bambu-studio" | grep -q 'not found'; then
  printf '%s\n' \
    'deb [trusted=yes] http://archive.ubuntu.com/ubuntu noble main universe' \
    'deb [trusted=yes] http://archive.ubuntu.com/ubuntu noble-updates main universe' \
    'deb [trusted=yes] http://security.ubuntu.com/ubuntu noble-security main universe' \
    > "$runtime_dir/apt/etc/sources.list"
  apt_opts=(
    -o APT::Sandbox::User=root
    -o Dir::Etc::sourcelist="$runtime_dir/apt/etc/sources.list"
    -o Dir::Etc::sourceparts=-
    -o Dir::State="$runtime_dir/apt/state"
    -o Dir::State::status=/var/lib/dpkg/status
    -o Dir::Cache="$runtime_dir/apt/cache"
  )
  apt-get "${apt_opts[@]}" update
  mapfile -t packages < <(read_pin debian_packages)
  apt-get -y "${apt_opts[@]}" --download-only --reinstall install "${packages[@]}"
  for package_file in "$runtime_dir"/apt/cache/archives/*.deb; do
    dpkg-deb -x "$package_file" "$runtime_dir/deps"
  done
fi

MUDMAN_BAMBU_RUNTIME_DIR="$runtime_dir" "$repo_root/scripts/run_bambu_studio.sh" --help >/dev/null
printf 'Bambu Studio %s runtime ready at %s\n' "$(read_pin version)" "$runtime_dir"
