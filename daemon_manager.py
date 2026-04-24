"""Download, launch, and stop mtga-tracker-daemon as a managed subprocess."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

RELEASES_LATEST = "https://api.github.com/repos/frcaton/mtga-tracker-daemon/releases/latest"
DEFAULT_PORT = 6842
LOCALHOST_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", ""})

HEADERS = {
    "User-Agent": "mtga-arena-exporter/0.1 (+https://github.com/uzimith/mtg-arena-exporter)",
    "Accept": "application/json",
}


def _platform_asset() -> tuple[str, str]:
    """Return (asset_name, exe_filename) for the current platform."""
    if sys.platform == "win32":
        return "mtga-tracker-daemon-Windows.zip", "mtga-tracker-daemon.exe"
    if sys.platform.startswith("linux"):
        return "mtga-tracker-daemon-Linux.tar.gz", "mtga-tracker-daemon"
    raise SystemExit(
        f"! mtga-tracker-daemon has no official build for platform {sys.platform!r}. "
        "Run the daemon manually and point --daemon at it, or pass --no-auto-daemon."
    )


def is_localhost(url: str) -> bool:
    host = urllib.parse.urlparse(url).hostname or ""
    return host.lower() in LOCALHOST_HOSTS


def parse_port(url: str) -> int:
    return urllib.parse.urlparse(url).port or DEFAULT_PORT


def is_daemon_running(base_url: str, timeout: float = 1.0) -> bool:
    url = base_url.rstrip("/") + "/cards"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except urllib.error.HTTPError:
        return True
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
        return False


def _download(url: str, dest: Path, accept: str = "*/*") -> None:
    headers = dict(HEADERS)
    headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=300) as r, dest.open("wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def _extract_archive(archive: Path, dest_dir: Path) -> None:
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest_dir)
    else:
        with tarfile.open(archive, "r:gz") as tf:
            tf.extractall(dest_dir)


def _find_exe(root: Path, exe_name: str) -> Path:
    direct = root / exe_name
    if direct.exists():
        return direct
    for p in root.rglob(exe_name):
        return p
    raise SystemExit(f"! {exe_name} not found under {root}")


def ensure_daemon_binary(cache_dir: Path, force_update: bool = False) -> Path:
    """Download and extract the daemon if needed, return path to executable."""
    asset_name, exe_name = _platform_asset()
    daemon_root = cache_dir / "daemon"
    daemon_root.mkdir(parents=True, exist_ok=True)
    version_file = daemon_root / "current_version.txt"

    if not force_update and version_file.exists():
        tag = version_file.read_text(encoding="utf-8").strip()
        candidate_dir = daemon_root / tag
        if candidate_dir.exists():
            try:
                exe = _find_exe(candidate_dir, exe_name)
                print(f"✓ using cached mtga-tracker-daemon {tag}")
                return exe
            except SystemExit:
                pass

    print("→ fetching mtga-tracker-daemon latest release info...")
    release = _fetch_json(RELEASES_LATEST)
    tag = release["tag_name"]
    asset = next((a for a in release["assets"] if a["name"] == asset_name), None)
    if asset is None:
        raise SystemExit(f"! release {tag} has no asset named {asset_name}")

    target_dir = daemon_root / tag
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True)

    archive = target_dir / asset_name
    size_mb = asset.get("size", 0) // (1024 * 1024)
    print(f"→ downloading {asset_name} ({size_mb} MB)...")
    _download(asset["browser_download_url"], archive)

    print(f"→ extracting to {target_dir}")
    _extract_archive(archive, target_dir)
    archive.unlink(missing_ok=True)

    exe = _find_exe(target_dir, exe_name)
    if sys.platform.startswith("linux"):
        exe.chmod(0o755)

    version_file.write_text(tag, encoding="utf-8")
    print(f"✓ installed mtga-tracker-daemon {tag}")
    return exe


def start_daemon(exe: Path, port: int, ready_timeout: float = 15.0) -> subprocess.Popen:
    print(f"→ starting mtga-tracker-daemon on port {port}")
    popen_kwargs: dict = {
        "cwd": str(exe.parent),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
    }
    if sys.platform == "win32":
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen([str(exe), "-p", str(port)], **popen_kwargs)

    base = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + ready_timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            tail = _read_tail(proc)
            raise SystemExit(
                f"! mtga-tracker-daemon exited early (code {proc.returncode}).\n{tail}"
            )
        if is_daemon_running(base, timeout=0.5):
            print("✓ daemon is ready")
            return proc
        time.sleep(0.5)

    stop_daemon(proc)
    tail = _read_tail(proc)
    raise SystemExit(
        f"! mtga-tracker-daemon did not become ready within {ready_timeout}s.\n{tail}"
    )


def _read_tail(proc: subprocess.Popen, max_bytes: int = 2048) -> str:
    if proc.stdout is None:
        return ""
    try:
        data = proc.stdout.read() or b""
    except Exception:
        return ""
    if len(data) > max_bytes:
        data = data[-max_bytes:]
    return data.decode("utf-8", errors="replace")


def stop_daemon(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    print("→ stopping mtga-tracker-daemon")
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=3)
