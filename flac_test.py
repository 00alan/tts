import subprocess

# This should print the version of FLAC if it's correctly recognized in the Python environment
result = subprocess.run(["flac", "-v"], capture_output=True, text=True)
print(result.stdout)
