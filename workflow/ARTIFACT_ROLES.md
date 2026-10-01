# Artifact Roles

- **Authoritative source:** the file or system that owns a design or process decision and must be changed to revise it.
- **Derived output:** a reproducible export, rendering, package, or metadata snapshot produced from authoritative sources.
- **Validation evidence:** recorded results showing that defined digital checks were run against an identified revision.
- **Release artifact:** the exact, intentionally retained output approved for delivery or production.
- **Physical validation evidence:** observations and results from testing an identified physical specimen under recorded conditions.

These roles may overlap only when a project says so explicitly. Distinguishing them prevents stale generated files from becoming accidental sources of truth and keeps an old digital pass or export from being mistaken for current physical or production approval.

For Bambu 3MF deliverables, also assign one of the mandatory artifact classes:
**Geometry 3MF**, **Configured Bambu Project 3MF**, or **Validated Print-Ready
Bambu 3MF**. Follow [Bambu 3MF Artifact Classes and Gates](BAMBU_3MF_ARTIFACTS.md);
package validity alone cannot promote an artifact to configured or print-ready.
