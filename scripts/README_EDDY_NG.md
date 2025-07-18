# Eddy-NG Installation Scripts

This directory contains scripts for integrating eddy-ng into a Klipper repository using git submodules.

## Overview

These scripts are designed for maintaining a Klipper fork with eddy-ng integration. They work with the eddy-ng submodule to automatically inject the necessary files and patches.

## Files

- `install_eddy_ng.py` - Main installation script for repository integration
- `install_eddy_ng.sh` - Shell wrapper script

## Usage

### Prerequisites

Ensure the eddy-ng submodule is properly initialized:

```bash
git submodule update --init --recursive
```

### Installation

```bash
# From the repository root
python3 scripts/install_eddy_ng.py

# Or using the shell wrapper
./scripts/install_eddy_ng.sh
```

### Uninstalling

```bash
python3 scripts/install_eddy_ng.py -u
```

### Specifying Target Directory

```bash
python3 scripts/install_eddy_ng.py /path/to/klipper/repo
```

## What It Does

### Files Copied

From the eddy-ng submodule to the main repository:

- `eddy-ng/probe_eddy_ng.py` → `klippy/extras/probe_eddy_ng.py`
- `eddy-ng/ldc1612_ng.py` → `klippy/extras/ldc1612_ng.py`
- `eddy-ng/eddy-ng/sensor_ldc1612_ng.c` → `src/sensor_ldc1612_ng.c`

### Patches Applied

1. **src/Makefile**: Adds `sensor_ldc1612_ng.c` to build when `CONFIG_WANT_LDC1612=y`
2. **klippy/extras/bed_mesh.py**: Modifies probe detection to recognize eddy-ng probes

### Whitespace Fixing

The script automatically fixes common whitespace issues in copied files:
- Removes trailing spaces
- Ensures proper line endings
- Attempts to break long lines where possible

## Automation

This script is used by the GitHub Actions workflow (`.github/workflows/update-fork.yml`) to automatically maintain the eddy-ng integration when the fork is updated.

## Key Features

- **Submodule Support**: Works with eddy-ng as a git submodule
- **Auto-detection**: Finds repository root automatically
- **Idempotent**: Safe to run multiple times
- **Smart Patching**: Checks if patches are already applied
- **Validation**: Ensures target is a valid Klipper repository
- **Whitespace Compliance**: Automatically fixes whitespace issues

## Building Firmware

After installation, enable eddy-ng support in your firmware build:

1. Run `make menuconfig`
2. Enable `CONFIG_WANT_LDC1612=y`
3. Build firmware with `make`

## Integration with Submodules

The script automatically:
- Locates the eddy-ng submodule at `eddy-ng/`
- Copies files from the submodule to the main repository
- Applies patches to integrate with Klipper
- Preserves the submodule relationship (files are copied, not moved)
- Fixes whitespace issues to meet Klipper standards

## Error Handling

The script includes error handling for:
- Missing submodule
- Invalid target directory
- Missing source files
- Already applied patches
- Whitespace issues

## Compatibility

Works with:
- Standard Klipper repositories
- Klipper forks
- Git submodules
- Both macOS and Linux (automatic sed detection) 