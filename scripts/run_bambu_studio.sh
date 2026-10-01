#!/usr/bin/env bash
set -euo pipefail

runtime_dir=${MUDMAN_BAMBU_RUNTIME_DIR:-/tmp/mudman-bambu-studio}
binary="$runtime_dir/app/bin/bambu-studio"
deps="$runtime_dir/deps"
[[ -x $binary ]] || { echo "Bambu runtime missing; run scripts/bootstrap_bambu_linux.sh" >&2; exit 2; }

export LD_LIBRARY_PATH="$runtime_dir/app/bin:$deps/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="$deps/usr/bin:$PATH"
export XDG_DATA_DIRS="$deps/usr/share:$runtime_dir/app/usr/share:/usr/share"
export LC_ALL=C
export LIBGL_ALWAYS_SOFTWARE=${LIBGL_ALWAYS_SOFTWARE:-1}
export GALLIUM_DRIVER=${GALLIUM_DRIVER:-llvmpipe}
export XDG_SESSION_TYPE=x11
export GDK_BACKEND=x11
export SDL_VIDEODRIVER=x11
unset WAYLAND_DISPLAY
runtime_state="$runtime_dir/state"
mkdir -p "$runtime_state/xdg" "$runtime_state/data" "$runtime_state/config"
chmod 700 "$runtime_state/xdg"
export XDG_RUNTIME_DIR="$runtime_state/xdg"
export XDG_DATA_HOME="$runtime_state/data"
export XDG_CONFIG_HOME="$runtime_state/config"

display=${MUDMAN_BAMBU_DISPLAY:-:98}
if [[ -n ${DISPLAY:-} ]]; then
  exec "$binary" "$@"
fi

xvfb=${MUDMAN_BAMBU_XVFB:-}
if [[ -z $xvfb ]]; then
  xvfb=$(command -v Xvfb || true)
fi
[[ -x $xvfb ]] || { echo "Xvfb missing from Bambu runtime" >&2; exit 2; }
"$xvfb" "$display" -screen 0 1280x1024x24 -nolisten tcp >"$runtime_state/xvfb.log" 2>&1 &
xvfb_pid=$!
trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT
export DISPLAY="$display"
for _ in 1 2 3 4 5; do
  [[ -S /tmp/.X11-unix/X${display#:} ]] && break
  sleep 0.2
done
"$binary" "$@"
