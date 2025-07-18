#!/usr/bin/env python3

import os
import sys
import argparse
import shutil
from pathlib import Path

IS_MAC = os.path.isdir("/System/Library")

SED_IN_PLACE_ARG = "-i ''" if IS_MAC else "-i"

# Files to copy for repo installation (relative to eddy-ng submodule)
FILES_TO_COPY = {
    "probe_eddy_ng.py": "klippy/extras",
    "ldc1612_ng.py": "klippy/extras",
    "eddy-ng/sensor_ldc1612_ng.c": "src"
}


def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))


def get_repo_root():
    """Find the repository root by looking for key Klipper files"""
    script_dir = get_script_dir()
    
    # Since we're in scripts/, the repo root should be parent directory
    potential_root = os.path.dirname(script_dir)
    
    # Look for key Klipper files to confirm we're in the right place
    klipper_markers = ["klippy", "src", "Makefile", "README.md"]
    
    if all(os.path.exists(os.path.join(potential_root, marker)) for marker in klipper_markers):
        return potential_root
    
    # Fallback: check current directory
    if all(os.path.exists(os.path.join(script_dir, marker)) for marker in klipper_markers):
        return script_dir
        
    return None


def get_eddy_ng_path(repo_root):
    """Get the path to the eddy-ng submodule"""
    return os.path.join(repo_root, "eddy-ng")


def uninstall_repo(target_dir: str):
    """Remove eddy-ng files from the repository"""
    print("Uninstalling eddy-ng from repository...")
    
    # Remove copied files
    for src_file, dest_dir in FILES_TO_COPY.items():
        dest_path = os.path.join(target_dir, dest_dir)
        dest_file = os.path.join(dest_path, os.path.basename(src_file))
        if os.path.isfile(dest_file):
            print(f"Removing {dest_file}")
            os.remove(dest_file)
        else:
            print(f"File {dest_file} does not exist. Skipping.")

    # Unpatch src/Makefile
    print("Unpatching src/Makefile...")
    makefile_path = os.path.join(target_dir, "src/Makefile")
    if os.path.exists(makefile_path):
        os.system(f"sed {SED_IN_PLACE_ARG} 's, sensor_ldc1612_ng.c,,' '{makefile_path}'")

    # Unpatch klippy/extras/bed_mesh.py
    print("Unpatching klippy/extras/bed_mesh.py...")
    bed_mesh_path = os.path.join(target_dir, "klippy/extras/bed_mesh.py")
    if os.path.exists(bed_mesh_path):
        os.system(
            f"sed {SED_IN_PLACE_ARG} 's,\"eddy\" in probe_name #eddy-ng,probe_name.startswith(\"probe_eddy_current\"),' '{bed_mesh_path}'"
        )
    
    print("eddy-ng uninstalled from repository.")


def install_repo(target_dir: str, uninstall: bool = False):
    """Install eddy-ng files into the repository"""
    
    if uninstall:
        uninstall_repo(target_dir)
        return

    print("Installing eddy-ng into repository...")
    print("=====================================")
    
    eddy_ng_path = get_eddy_ng_path(target_dir)
    
    if not os.path.exists(eddy_ng_path):
        print(f"Error: eddy-ng submodule not found at {eddy_ng_path}")
        print("Make sure the eddy-ng submodule is properly initialized:")
        print("  git submodule update --init --recursive")
        sys.exit(1)
    
    # Copy files to their destinations
    for src_file, dest_dir in FILES_TO_COPY.items():
        src_path = os.path.join(eddy_ng_path, src_file)
        dest_path = os.path.join(target_dir, dest_dir)
        dest_file = os.path.join(dest_path, os.path.basename(src_file))

        if not os.path.exists(src_path):
            print(f"Warning: Source file {src_path} does not exist. Skipping.")
            continue

        if not os.path.exists(dest_path):
            print(f"Warning: Destination directory {dest_path} does not exist. Skipping.")
            continue

        print(f"Copying {src_file} to {dest_dir}/")
        shutil.copyfile(src_path, dest_file)

    # Patch src/Makefile
    print("Patching src/Makefile...")
    makefile_path = os.path.join(target_dir, "src/Makefile")
    if os.path.exists(makefile_path):
        # Check if already patched
        with open(makefile_path, 'r') as f:
            content = f.read()
        
        if "sensor_ldc1612_ng.c" not in content:
            os.system(f"sed {SED_IN_PLACE_ARG} 's,sensor_ldc1612.c$,sensor_ldc1612.c sensor_ldc1612_ng.c,' '{makefile_path}'")
            print("Makefile patched successfully.")
        else:
            print("Makefile already patched.")
    else:
        print("Warning: src/Makefile not found.")

    # Patch klippy/extras/bed_mesh.py
    print("Patching klippy/extras/bed_mesh.py...")
    bed_mesh_path = os.path.join(target_dir, "klippy/extras/bed_mesh.py")
    if os.path.exists(bed_mesh_path):
        # Check if already patched
        with open(bed_mesh_path, 'r') as f:
            content = f.read()
        
        if "#eddy-ng" not in content:
            os.system(
                f"sed {SED_IN_PLACE_ARG} 's,probe_name.startswith(\"probe_eddy_current\"),\"eddy\" in probe_name #eddy-ng,' '{bed_mesh_path}'"
            )
            print("bed_mesh.py patched successfully.")
        else:
            print("bed_mesh.py already patched.")
    else:
        print("Warning: klippy/extras/bed_mesh.py not found.")

    print("")
    print("Installation complete!")
    print("======================")
    print("Files have been copied into the repository.")
    print("When building firmware, make sure to enable CONFIG_WANT_LDC1612=y")
    print("in your configuration to include the eddy-ng sensor support.")


def main():
    parser = argparse.ArgumentParser(
        description="Install eddy-ng into Klipper repository (for maintaining forks)"
    )
    parser.add_argument(
        "-u", "--uninstall", 
        action="store_true", 
        help="Uninstall eddy-ng from repository"
    )
    parser.add_argument(
        "target_dir", 
        nargs="?", 
        help="Target repository directory (defaults to auto-detected repo root)"
    )

    args = parser.parse_args()

    target_dir = args.target_dir
    uninstall = args.uninstall

    # Auto-detect repository root if not provided
    if not target_dir:
        target_dir = get_repo_root()
        if not target_dir:
            print("Error: Could not auto-detect Klipper repository root.")
            print("Please specify the target directory manually.")
            sys.exit(1)
        print(f"Auto-detected repository root: {target_dir}")

    # Validate target directory
    if not os.path.isdir(target_dir):
        print(f"Error: Target directory '{target_dir}' does not exist.")
        sys.exit(1)

    # Check if it looks like a Klipper repository
    required_dirs = ["src", "klippy", "klippy/extras"]
    missing_dirs = [d for d in required_dirs if not os.path.exists(os.path.join(target_dir, d))]
    
    if missing_dirs:
        print(f"Error: Target directory doesn't appear to be a Klipper repository.")
        print(f"Missing directories: {', '.join(missing_dirs)}")
        sys.exit(1)

    # Run installation
    install_repo(target_dir, uninstall)


if __name__ == "__main__":
    main() 