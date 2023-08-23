# Count the number of host reads found/removed from Shotgun data
# Produce a table with sample IDS and counts

# Run in Summaries directory

import pandas as pd
import glob
import os

# Set up lists
# Lists are populated with info read from file
# Lists are then pulled into pandas database


SAMPLEIDS = []
HOSTCOUNTS = []

# Find input files

FILES = glob.glob("../Hostcheck/*hostIDs.txt")

for file in FILES:
	#Save filename
	path = os.path.dirname(file)
	fname = os.path.basename(file)
	#Extract project ID (2 letter code)
	pid = fname.split("_")[0]
	#Extract sampleID
	sid = fname.split("_")[1]

	with open(file, 'r') as fileObj:
		num_lines = sum(1 for line in fileObj)

	psid = pid + "_" + sid
	HOSTCOUNTS.append(num_lines)
	SAMPLEIDS.append(psid)

df_host = pd.DataFrame({
	'SampleID':SAMPLEIDS,
	'Num_hostreads':HOSTCOUNTS
	})

df_host.to_csv('hostcheck_summary.txt', sep = "\t", index = False)
