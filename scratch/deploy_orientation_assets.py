import os
import shutil

src_dir = os.path.abspath("scratch/orientation_screenshots")
dest_dirs = [
    os.path.abspath("kwara_cbt_app/static/images/orientation"),
    os.path.abspath("public/static/images/orientation"),
    os.path.abspath("static/images/orientation")
]

for d in dest_dirs:
    os.makedirs(d, exist_ok=True)
    for fname in os.listdir(src_dir):
        if fname.endswith(".png"):
            src_f = os.path.join(src_dir, fname)
            dest_f = os.path.join(d, fname)
            shutil.copy2(src_f, dest_f)
            print(f"Copied {fname} -> {dest_f}")

print("All orientation screenshots copied to static directories!")
