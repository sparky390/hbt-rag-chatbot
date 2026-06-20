#!/usr/bin/env python3
import os
import sys
import pwd
import shutil

def chown_path(path, uid, gid):
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except Exception:
            return
    for root, dirs, files in os.walk(path):
        try:
            os.chown(root, uid, gid)
        except Exception:
            pass
        for name in files:
            try:
                os.chown(os.path.join(root, name), uid, gid)
            except Exception:
                pass


def main():
    # determine appuser uid/gid
    try:
        pw = pwd.getpwnam("appuser")
        uid = pw.pw_uid
        gid = pw.pw_gid
    except KeyError:
        uid = os.getuid()
        gid = os.getgid()

    # Ensure data and chroma dirs exist and are owned by appuser
    chown_path("/app/data", uid, gid)
    chown_path("/app/chroma_db", uid, gid)

    # Drop privileges to appuser
    try:
        os.setgid(gid)
        os.setuid(uid)
    except Exception:
        pass

    # Build command: streamlit run app.py + any CMD args passed
    cmd = ["streamlit", "run", "app.py"] + sys.argv[1:]
    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
