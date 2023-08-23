from os import rename
from glob import glob

FNAMES = glob('*L00*_R*_001.fastq.gz')

print(FNAMES)

for fname in FNAMES:
  sample = fname.split("_")[0]
  prefix = fname.split("_")[1]
  fwdrev = fname.split("_")[5]
  
  newname = f"{prefix}_{sample}_{fwdrev}.fastq.gz"
  
  rename(fname, newname)
  
  print(f"{fname} has been renamed to {newname}")
