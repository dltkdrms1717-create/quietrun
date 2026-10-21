# -*- coding: utf-8 -*-
"""orphan_driver_sweep — kill chromedriver.exe / msedgedriver.exe processes whose parent is gone.

Why: when a Selenium script dies without ``driver.quit()``, the WebDriver process (and the
browser it spawned) keeps running and holds the parent console window open.  On an unattended
Windows box this piles up to dozens of zombie drivers and console windows within a few weeks.

What it does: lists driver processes whose *parent PID no longer exists*, plus the browser
children they spawned, and kills only those.  Live automation jobs (parent still alive) are
never touched.  Safe to schedule every 30 minutes with ``quietrun.py`` / ``pythonw.exe``.

Usage:
    python orphan_driver_sweep.py            # kill orphans, append a line to orphan_driver_sweep.log
    python orphan_driver_sweep.py --dry-run  # only report, kill nothing

Requires Windows + PowerShell 5.1+ + Python 3.8+.  No third-party packages.
"""
import subprocess, sys, os, json, time, io

CREATE_NO_WINDOW = 0x08000000
DRIVERS = ("chromedriver.exe", "msedgedriver.exe", "geckodriver.exe")
PS = r"""
$all = Get-CimInstance Win32_Process; $by=@{}; foreach($p in $all){$by[[int]$p.ProcessId]=$p}
$out=@()
foreach($p in ($all | Where-Object { @('chromedriver.exe','msedgedriver.exe','geckodriver.exe') -contains $_.Name })){
  if($null -eq $by[[int]$p.ParentProcessId]){
    $kids = @($all | Where-Object { ($_.Name -eq 'chrome.exe' -or $_.Name -eq 'msedge.exe' -or $_.Name -eq 'firefox.exe') -and [int]$_.ParentProcessId -eq [int]$p.ProcessId } | ForEach-Object { [int]$_.ProcessId })
    $out += @{ pid=[int]$p.ProcessId; name=$p.Name; start=$p.CreationDate.ToString('MM-dd HH:mm'); kids=$kids }
  }
}
ConvertTo-Json -Compress -Depth 3 @($out)
"""


def orphans():
    r = subprocess.run(["powershell", "-NoProfile", "-Command", PS], capture_output=True, text=True,
                       creationflags=CREATE_NO_WINDOW, timeout=120)
    s = (r.stdout or "").strip()
    j = json.loads(s) if s else []
    return [j] if isinstance(j, dict) else j


def main():
    dry = "--dry-run" in sys.argv
    found = orphans()
    log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orphan_driver_sweep.log")
    killed = []
    for o in found:
        for pid in list(o.get("kids") or []) + [o["pid"]]:
            if not dry:
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, creationflags=CREATE_NO_WINDOW)
            killed.append(pid)
    line = time.strftime("%Y-%m-%d %H:%M") + (" dry-run" if dry else "") + " orphans=%d pids=%s" % (len(found), killed)
    if found or dry:
        with io.open(log, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    print(line)


if __name__ == "__main__":
    main()
