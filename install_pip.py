import urllib.request
import subprocess
import sys

print("Downloading get-pip.py...")
urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
print("Installing pip...")
subprocess.check_call([sys.executable, "get-pip.py"])
print("Done! Now run: py -m pip install boto3")
