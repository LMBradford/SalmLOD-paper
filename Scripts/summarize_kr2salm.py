# Count the number of putative Salmonella hits from Kraken2 output
# Produce a table with sample IDS and counts

# Run in Summaries directory

import pandas as pd
import glob
import os

# Set up lists
# Lists are populated with info read from file
# Lists are then pulled into pandas database

FILENAMES, SAMPLEIDS = [], []
SALMCOUNTS = []

# Find input files

FILES = glob.glob("../Salmonella/*salmhitIDs.txt")

for file in FILES:
	#Save filename
	path = os.path.dirname(file)
	fname = os.path.basename(file)
	#Extract project ID (2 letter code)
	pid = fname.split("_")[0]
	#Extract sampleID
	sid = fname.split("_")[1]

	psid = pid + "_" + sid

	with open(file, 'r') as fileObj:
		num_lines = sum(1 for line in fileObj)

	SALMCOUNTS.append(num_lines)
	SAMPLEIDS.append(psid)

df_kr2salm = pd.DataFrame({
	'SampleID':SAMPLEIDS,
	'Kr2_putSalmHits':SALMCOUNTS
	})

df_kr2salm.to_csv('kr2salmhits_summary.txt', sep = "\t", index = False)
