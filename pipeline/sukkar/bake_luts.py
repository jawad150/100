"""Bake one 65^3 grading LUT per B-roll clip (technical S-Log3 -> Rec.709 + look + clip trims),
plus a shareable 33^3 show LUT without per-clip trims."""
import os

import clipgrades
import grade

os.makedirs("luts", exist_ok=True)
for clip in clipgrades.TRIM:
    grade.write_cube(f"luts/{clip}.cube", clipgrades.params(clip))
    print("luts/" + clip + ".cube")
show = dict(clipgrades.LOOK)
show.update(exposure=-0.4, wb=(1.0, 1.0, 1.0))
grade.write_cube("luts/SukkarReel_SLog3-SGamut3Cine_to_Rec709_look.cube", show, n=33)
