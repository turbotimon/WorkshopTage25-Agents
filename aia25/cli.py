def main():
    import subprocess

    subprocess.run(["chainlit", "run", "aia25/app.py", "-w", "-h"], check=True)
