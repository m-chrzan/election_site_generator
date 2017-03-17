import os
import subprocess

def get_data():
    """Executes a bash script that downloads the necessary data into data/."""
    if not os.path.isdir("data"):
        subprocess.run("bin/get_data.sh")

if __name__ == '__main__':
    get_data()
