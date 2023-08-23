# Count the number of confirmed Salmonella hits from SSR check output
# Produce a table with sample IDS and counts

# Run in Summaries directory

import pandas as pd
import glob
import os

# Set up lists
# Lists are populated with info read from file
# Lists are then pulled into pandas database

SAMPLEIDS = []
SALMCOUNTS = []

# Find input files

FILES = glob.glob("../Salmonella/SSRchecks/*salmSSRhits.txt")

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

df_SSRsalm = pd.DataFrame({
	'SampleID':SAMPLEIDS,
	'SSR_SalmHits':SALMCOUNTS
	})

df_SSRsalm.to_csv('ssr-salmhits_summary.txt', sep = "\t", index = False)
