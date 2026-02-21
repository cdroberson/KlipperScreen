# KlipperScreen Fork Notes

## What's Changed from Upstream

### New Panels
- **Print History** (`panels/print_history.py`) - Shows past prints from Moonraker history API
- **Quick Positions** (`panels/quick_positions.py`) - Configurable one-tap position buttons

### Enhancements
- **Disk Space** (`panels/system.py`) - Progress bar in System panel
- **Fan RPM** (`panels/fan.py`, `panels/job_status.py`) - Shows RPM when tachometer data available
- **Config validation** (`ks_includes/config.py`) - Registered `[quick_positions]` section

### Themes
- **struan-dark** - Modern dark theme (blue/purple/green/gold accents)
- **struan-light** - Modern light theme (matching palette)
- Both include 104 recolored SVG icons

## Quick Positions Config

Add to `KlipperScreen.conf` (above the auto-generated line):

```ini
[quick_positions]
Center: 0, 0, 50
Load Filament: 0, 0, 100
```

Format: `Name: X, Y, Z`

## Syncing with Upstream

```bash
git fetch upstream
git rebase upstream/master
git push --force-with-lease origin master
```

Then on the Pi:
```bash
cd ~/KlipperScreen2 && git pull && sudo systemctl restart KlipperScreen
```

## Pi Setup

- **Install path:** `/home/pi/KlipperScreen2/`
- **Service file:** `/etc/systemd/system/KlipperScreen.service`
- **Config file:** `~/.config/KlipperScreen/KlipperScreen.conf`
- **Virtualenv:** `/home/pi/.KlipperScreen-env/`
- **Moonraker config:** `[update_manager KlipperScreen]` in moonraker.conf points to this repo

## Remotes

- `origin` - `github.com/cdroberson/KlipperScreen.git` (your fork)
- `upstream` - `github.com/KlipperScreen/KlipperScreen.git` (original)
