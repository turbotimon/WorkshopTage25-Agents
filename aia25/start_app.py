def main():
    import subprocess

    subprocess.run(["chainlit", "run", "aia25/ui/app.py", "-w", "-h"], check=True)
