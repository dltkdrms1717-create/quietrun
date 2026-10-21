# -*- coding: utf-8 -*-
"""quietrun — run a Python script from Windows Task Scheduler without a console window.

Why: when Task Scheduler launches ``py.exe``/``.bat`` directly, a black console window
flashes (or stays) on the signed-in user's desktop.  Launching this file with ``pythonw.exe``
instead gives you: no window, stdout/stderr appended to a log file, a start/end stamp with
the exit code, and the child's exit code passed through.

Usage (Task Scheduler "Program" / "Arguments"):

    pythonw.exe  -X utf8 C:\\tools\\quietrun.py  C:\\jobs\\job.py  C:\\jobs\\job.log  [C:\\jobs]

Arguments: <script.py> <logfile> [working-dir].  Exit code = the script's exit code
(2 if arguments are missing).  Requires Windows + Python 3.8+.
"""
import sys, os, subprocess, datetime

CREATE_NO_WINDOW = 0x08000000


def main():
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__)
        sys.exit(2)
    script, log = sys.argv[1], sys.argv[2]
    cwd = sys.argv[3] if len(sys.argv) > 3 else (os.path.dirname(os.path.abspath(script)) or os.getcwd())
    # Prefer the console-less interpreter's sibling python.exe so the child inherits the same environment.
    py = os.path.join(os.path.dirname(sys.executable), "python.exe")
    if not os.path.exists(py):
        py = sys.executable
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    with open(log, "ab") as f:
        f.write(("\n=== %s start %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), os.path.basename(script))).encode("utf-8"))
        f.flush()
        rc = subprocess.call([py, "-X", "utf8", script], cwd=cwd, stdout=f, stderr=subprocess.STDOUT, env=env,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", CREATE_NO_WINDOW))
        f.write(("=== %s end exit=%s\n" % (datetime.datetime.now().strftime("%H:%M:%S"), rc)).encode("utf-8"))
    sys.exit(rc)


if __name__ == "__main__":
    main()
