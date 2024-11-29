import hashlib
import os

# Path to your syzygy folder
syzygy_folder = 'C:\\Users\\User\\Desktop\\AI\\Projects\\Smart-Chess\\syzygy'  # Replace with the actual path

# Path to the checksum.md5 file
checksum_file = os.path.join(syzygy_folder, 'checksum.md5')

# Function to compute the MD5 checksum of a file
def compute_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        # Read the file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Read the checksums from checksum.md5
checksums = {}
with open(checksum_file, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        checksum, filename = line.split()
        # Remove any leading '*' or ' ' from filename
        filename = filename.lstrip('* ')
        checksums[filename] = checksum.lower()

# List all .rtbz and .rtbw files in the syzygy folder
file_list = [f for f in os.listdir(syzygy_folder) if f.endswith('.rtbz') or f.endswith('.rtbw')]

# Check the checksums
for filename in file_list:
    file_path = os.path.join(syzygy_folder, filename)
    if filename in checksums:
        print(f'Checking {filename}...')
        md5_checksum = compute_md5(file_path).lower()
        if md5_checksum == checksums[filename]:
            # print(f'{filename}: OK')
            pass
        else:
            print(f'{filename}: FAILED')
            print(f'Expected: {checksums[filename]}')
            print(f'Actual  : {md5_checksum}')
    else:
        print(f'{filename}: No checksum found in checksum.md5')
