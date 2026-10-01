#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$ROOT/bambu-runtime.json")"
CACHE_ROOT="${MUDMAN_BAMBU_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/mudman-fabrication/bambu-studio}"
RUNTIME_ROOT="$CACHE_ROOT/$VERSION"; APPDIR="$RUNTIME_ROOT/squashfs-root"; SYSROOT="$RUNTIME_ROOT/apt-root/sysroot"; DEPS="$RUNTIME_ROOT/deps"
[[ -x "$APPDIR/bin/bambu-studio" ]] || { echo "Run scripts/bootstrap_bambu_linux.sh first" >&2; exit 1; }
unset PYTHONHOME PYTHONPATH
export LIBGL_ALWAYS_SOFTWARE=1
export XDG_SESSION_TYPE=wayland
export GDK_BACKEND=wayland
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/mudman-bambu-runtime-${UID}}"
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
DEFAULT_XKB_ROOT="$SYSROOT/usr/share/X11/xkb"
[[ -d "$DEFAULT_XKB_ROOT" ]] || DEFAULT_XKB_ROOT=/usr/share/X11/xkb
export LC_ALL=C LD_LIBRARY_PATH="$APPDIR/bin:$DEPS" XKB_CONFIG_ROOT="${XKB_CONFIG_ROOT:-$DEFAULT_XKB_ROOT}"
export XDG_DATA_DIRS="${XDG_DATA_DIRS:-$SYSROOT/usr/share:$APPDIR/usr/share:/usr/share}" FONTCONFIG_PATH="${FONTCONFIG_PATH:-$SYSROOT/etc/fonts}"

if [[ -n "${WAYLAND_DISPLAY:-}" && -S "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" ]]; then
  exec "$APPDIR/bin/bambu-studio" "$@"
fi

WESTON="$SYSROOT/usr/bin/weston"
WESTON_BACKEND="$SYSROOT/usr/lib/x86_64-linux-gnu/libweston-13/headless-backend.so"
WESTON_LIBS="$SYSROOT/usr/lib/x86_64-linux-gnu/weston:$SYSROOT/usr/lib/x86_64-linux-gnu:$SYSROOT/lib/x86_64-linux-gnu"
[[ -x "$WESTON" && -f "$WESTON_BACKEND" ]] || {
  echo "Headless Weston is missing; rerun scripts/bootstrap_bambu_linux.sh" >&2
  exit 1
}

WAYLAND_DISPLAY="mudman-bambu-${UID}-$$"
export WAYLAND_DISPLAY
WESTON_LOG="$XDG_RUNTIME_DIR/${WAYLAND_DISPLAY}.log"
WESTON_MODULE_MAP="headless-backend.so=$WESTON_BACKEND;" \
  LD_LIBRARY_PATH="$WESTON_LIBS" \
  "$WESTON" --backend=headless --renderer=pixman --socket="$WAYLAND_DISPLAY" \
  --idle-time=0 --no-config --log="$WESTON_LOG" &
WESTON_PID=$!
cleanup() {
  kill "$WESTON_PID" 2>/dev/null || true
  wait "$WESTON_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

for _ in $(seq 1 50); do
  [[ -S "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" ]] && break
  kill -0 "$WESTON_PID" 2>/dev/null || break
  sleep 0.1
done
if [[ ! -S "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" ]]; then
  echo "Bambu runtime unavailable: headless Wayland socket could not be created." >&2
  echo "The host must permit Unix-domain sockets in XDG_RUNTIME_DIR." >&2
  [[ -f "$WESTON_LOG" ]] && tail -40 "$WESTON_LOG" >&2
  exit 1
fi

set +e
"$APPDIR/bin/bambu-studio" "$@"
STATUS=$?
set -e
exit "$STATUS"
