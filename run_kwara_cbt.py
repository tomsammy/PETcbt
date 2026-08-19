import os
import sys
import subprocess

app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kwara_cbt_app")
sys.path.insert(0, app_dir)

if __name__ == "__main__":
    from run_cbt import main
    main()
