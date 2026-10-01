"""Generate the rigid Small project through the pinned Linux Bambu writer.

Run this file with FreeCADCmd. It is project-specific parity evidence for the
shared runtime, not a replacement for the round-mold-insert production source.
"""
import os, sys
from pathlib import Path

repo=Path(os.environ["ROUND_MOLD_REPO"]).resolve(); sys.path.insert(0,str(repo))
import FreeCAD as App
from potvessel.features import create_sand_casting_mold
import potvessel.export as export
export.BAMBU_PROFILE_ROOT=str(Path(os.environ["BAMBU_PROFILE_ROOT"]).resolve())
doc=App.newDocument("RigidSmallCloudParity")
mold=create_sand_casting_mold(doc,"Cylinder Small","SandCastingMoldSmall")
output=Path(os.environ["PARITY_OUTPUT"]).resolve()
doc.recompute(); output.parent.mkdir(parents=True,exist_ok=True)
export.export_bambu_production_mold(mold,str(output))
print(output)
