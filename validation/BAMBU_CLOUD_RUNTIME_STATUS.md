# Cloud Bambu Runtime Status

- Candidate Bambu Studio: `02.08.02.61`
- Platform: Ubuntu 24.04 x86-64 AppImage
- AppImage SHA-256: `d501b103fac5424513ec0e8d6bc145fb30719de2c7d94d7320d723740c81a7fd`
- Headless compositor: Weston 13, Pixman renderer
- Promotion status: **NOT PROMOTED / PARITY INCOMPLETE**

The official binary was downloaded, hash-verified, extracted without FUSE, and
its help output confirmed the presence of `--load-settings`,
`--load-filaments`, `--export-3mf`, and `--slice`.

The current ChatGPT Work execution sandbox does not permit Weston to create its
Unix-domain Wayland socket. Consequently Bambu cannot execute a real export or
slice here. Xvfb is not a substitute because this AppImage's bundled GLFW uses
the Wayland backend.

The exact private golden rigid Small project also must be available to the
parity job. Recorded audit data or regenerated geometry is not an acceptable
replacement for loading, re-exporting, reopening, and slicing that exact
artifact.

Until both blockers are removed, the runtime must not generate authoritative
configured projects, the rigid parity result is **NOT RUN**, and the Flexible
V0 pilot remains a **GEOMETRY 3MF** requiring authoritative Bambu Studio work.
