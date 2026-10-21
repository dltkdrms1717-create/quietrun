# quietrun

Two tiny, dependency-free helpers for running unattended Python automation on **Windows** without the usual mess.

| File | Problem it solves |
|---|---|
| `quietrun.py` | Task Scheduler jobs that call `py.exe` / `.bat` flash (or leave) a black console window on the user's desktop. `quietrun.py` runs the script with no window, appends stdout/stderr to a log, stamps start/end + exit code, and passes the exit code through. |
| `orphan_driver_sweep.py` | Selenium scripts that die without `driver.quit()` leave `chromedriver.exe` / `msedgedriver.exe` zombies (and their browsers) behind — we once found 21 of them. The sweeper kills **only** drivers whose parent process is gone, never live jobs. |

Born on a fleet of always-on Windows PCs that run scheduled scrapers and browser automation 24/7; both scripts have been in production since 2026-09.

## Install

Copy the two files anywhere, e.g. `C:\tools\`. Python 3.8+ and PowerShell 5.1+ (built into Windows). No packages to install.

## quietrun.py

Task Scheduler → Action → *Start a program*:

```
Program:    C:\Users\me\AppData\Local\Programs\Python\Python311\pythonw.exe
Arguments:  -X utf8 C:\tools\quietrun.py C:\jobs\report.py C:\jobs\report.log C:\jobs
```

- Uses `pythonw.exe` (no console) and launches the child with `CREATE_NO_WINDOW`.
- Log line format: `=== 2026-10-22 06:00:01 start report.py` … `=== 06:00:09 end exit=0`.
- Exit code of the job is returned, so Task Scheduler's *Last Run Result* stays meaningful.

## orphan_driver_sweep.py

```
python orphan_driver_sweep.py --dry-run   # list what would be killed
python orphan_driver_sweep.py             # kill orphans, log to orphan_driver_sweep.log
```

Schedule it every 30 minutes with `quietrun.py`. It looks for `chromedriver.exe`, `msedgedriver.exe`, `geckodriver.exe` whose **parent PID no longer exists**, kills them and the `chrome.exe` / `msedge.exe` / `firefox.exe` children they spawned. Anything with a living parent is untouched.

## Lessons baked in

- `cmd.exe /c "python" ... > "log"` strips the outer quotes and silently runs nothing — launch Python directly, never through `cmd /c` with quoted paths.
- A child that inherits the parent's stdio handles can keep a remote-execution agent blocked until it exits; redirect to a file or detach.

## 한국어

윈도우 예약작업으로 파이썬 자동화를 돌릴 때 생기는 두 가지 골칫거리를 없애는 작은 도구입니다.

- **quietrun.py** — 예약작업이 `py.exe`/`.bat`를 직접 부르면 사용자 화면에 검은 콘솔창이 뜹니다. 이 파일을 `pythonw.exe`로 띄우면 창 없이 돌고, 출력은 로그 파일에 쌓이며, 시작·끝 시각과 종료코드가 한 줄씩 남습니다.
- **orphan_driver_sweep.py** — 셀레늄 스크립트가 `driver.quit()` 없이 죽으면 `chromedriver.exe`가 좀비로 남아 콘솔창을 붙들고 있습니다(한 PC에서 21개가 쌓인 적이 있습니다). 부모 프로세스가 죽은 드라이버와 그 밑 브라우저만 정리하고, 살아 있는 작업은 건드리지 않습니다. `--dry-run`으로 먼저 확인할 수 있습니다.

## License

MIT
