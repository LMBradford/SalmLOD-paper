# Read the first line of all Kraken2 reports in a directory
# Save the percent of reads unclassified
# Produce a table of sampleID + percent unclassified

# Run in Summaries directory

import pandas as pd #for dataframes
import glob
import os

# Set up lists
# Lists are populated with info read from file
# Lists are then pulled into pandas database

FILENAMES, SAMPLEIDS = [], []
UNCLASSPERCS = []

# Find input files

FILES = glob.glob("../Kr2reports/*_paired.kr2bac_c0.25.kr2rep")

# Loop through input files
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
		first_line = fileObj.readline().rstrip()
		#Reads just the first line from the file
		#strips newline character from end of line

	unclass_perc = first_line.partition('\t')[0]

	SAMPLEIDS.append(psid)
	UNCLASSPERCS.append(unclass_perc)

df_kr2rep = pd.DataFrame({
	'SampleID':SAMPLEIDS,
	'Percent_unclassified':UNCLASSPERCS
	})

#Convert datatype and add column for percent classified
df_kr2rep['Percent_unclassified'] = pd.to_numeric(df_kr2rep['Percent_unclassified'])
df_kr2rep['Percent_classified'] = 100 - df_kr2rep['Percent_unclassified']

#Round to 2 decimal points
df_kr2rep = df_kr2rep.round({'Percent_classified': 2})

df_kr2rep.to_csv('kr2rep_summary.txt', sep = "\t", index = False)
