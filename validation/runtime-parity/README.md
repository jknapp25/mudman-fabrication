# Runtime parity evidence

Do not commit generated candidate projects, G-code, or slicer scratch output in
this directory. Commit only concise parity reports containing the source and
result hashes, Bambu version, preserved-setting assertions, package comparison,
warning status, and slice result.

Cloud Bambu authority requires the exact known-good rigid Small project as the
input. Regenerating a similar project from CAD is useful diagnostic evidence but
does not satisfy exact-golden parity.
