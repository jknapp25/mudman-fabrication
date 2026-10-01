#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_JSON="$ROOT/bambu-runtime.json"
CACHE_ROOT="${MUDMAN_BAMBU_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/mudman-fabrication/bambu-studio}"
read_runtime() { python3 - "$RUNTIME_JSON" "$1" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as stream: print(json.load(stream)[sys.argv[2]])
PY
}
VERSION="$(read_runtime version)"; URL="$(read_runtime appimage_url)"; EXPECTED_SHA="$(read_runtime appimage_sha256)"
RUNTIME_ROOT="$CACHE_ROOT/$VERSION"; APPIMAGE="$RUNTIME_ROOT/BambuStudio.AppImage"; APPDIR="$RUNTIME_ROOT/squashfs-root"
APT_ROOT="$RUNTIME_ROOT/apt-root"; SYSROOT="$APT_ROOT/sysroot"; DEPS="$RUNTIME_ROOT/deps"
mkdir -p "$RUNTIME_ROOT"
[[ -f "$APPIMAGE" ]] || curl -fL --retry 3 -o "$APPIMAGE" "$URL"
ACTUAL_SHA="$(sha256sum "$APPIMAGE" | awk '{print $1}')"
[[ "$ACTUAL_SHA" == "$EXPECTED_SHA" ]] || { echo "Bambu AppImage digest mismatch" >&2; exit 1; }
chmod +x "$APPIMAGE"
[[ -x "$APPDIR/bin/bambu-studio" ]] || (cd "$RUNTIME_ROOT" && "$APPIMAGE" --appimage-extract >/dev/null)
missing="$(LD_LIBRARY_PATH="$APPDIR/bin" ldd "$APPDIR/bin/bambu-studio" | awk '/not found/{print $1}')"
if [[ -n "$missing" ]] || [[ ! -x "$SYSROOT/usr/bin/weston" ]]; then
  command -v apt-get >/dev/null; command -v dpkg-deb >/dev/null
  mkdir -p "$APT_ROOT/var/lib/dpkg" "$APT_ROOT/var/cache/apt/archives/partial" "$SYSROOT" "$DEPS"
  if [[ -f /var/lib/dpkg/status ]]; then cp /var/lib/dpkg/status "$APT_ROOT/var/lib/dpkg/status"; else : > "$APT_ROOT/var/lib/dpkg/status"; fi
  apt-get -o APT::Sandbox::User=root update
  apt-get -o APT::Sandbox::User=root -o Dir::State::status="$APT_ROOT/var/lib/dpkg/status" \
    -o Dir::Cache::archives="$APT_ROOT/var/cache/apt/archives" --download-only install -y \
    weston dbus-x11 libwebkit2gtk-4.1-0 libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 libwayland-server0
  for package in "$APT_ROOT"/var/cache/apt/archives/*.deb; do dpkg-deb -x "$package" "$SYSROOT" || true; done
  ldconfig -p | awk '{print $1}' | sort -u > "$RUNTIME_ROOT/system-libs.txt"
  find "$SYSROOT/usr/lib/x86_64-linux-gnu" "$SYSROOT/lib/x86_64-linux-gnu" -maxdepth 1 \
    \( -type f -o -type l \) -name '*.so*' -print 2>/dev/null | while read -r library; do
      name="$(basename "$library")"; grep -qxF "$name" "$RUNTIME_ROOT/system-libs.txt" || ln -sfn "$library" "$DEPS/$name"
    done || true
fi
python3 "$ROOT/scripts/probe_bambu_runtime.py" >/dev/null
printf 'BAMBU_STUDIO_VERSION=%s\nBAMBU_STUDIO_APPIMAGE_SHA256=%s\nBAMBU_STUDIO_ROOT=%s\n' \
  "$VERSION" "$ACTUAL_SHA" "$RUNTIME_ROOT" > "$RUNTIME_ROOT/runtime.env"
echo "$RUNTIME_ROOT"
