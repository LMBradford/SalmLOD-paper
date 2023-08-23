# Summarize trimlog files from Trimmomatic output
# Produces a single table

# Run in Summaries directory

import pandas as pd #for dataframes
import glob
import os

# Set up lists
# Lists are populated with info read from file
# Lists are then pulled into pandas database

FILENAMES, SAMPLEIDS = [], []
INPUTREADS = []
PAIRNUMS, PAIRPERCENTS = [], []
FWDNUMS, FWDPERCENTS = [], []
REVNUMS, REVPERCENTS = [], []
DROPNUMS, DROPPERCENTS = [], []


# Find input files

FILES = glob.glob("../Trimlogs/*trimlog.txt") #Files must be in working directory

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
		LINES = fileObj.readlines() 
		#Reads whole file into memory
		#Each new line is object in list LINES

	#For each line:
	## strip newline from right (rstrip)
	## take value after the colon (partition)

	inputread = LINES[0].rstrip().partition(": ")[2]
	pairnum = LINES[1].rstrip().partition(": ")[2]
	pairperc = LINES[2].rstrip().partition(": ")[2]
	fwdnum = LINES[3].rstrip().partition(": ")[2]
	fwdperc = LINES[4].rstrip().partition(": ")[2]
	revnum = LINES[5].rstrip().partition(": ")[2]
	revperc = LINES[6].rstrip().partition(": ")[2]
	dropnum = LINES[7].rstrip().partition(": ")[2]
	dropperc = LINES[8].rstrip().partition(": ")[2]

	#Populate lists w values from each file
	FILENAMES.append(fname)
	SAMPLEIDS.append(psid)
	INPUTREADS.append(inputread)
	PAIRNUMS.append(pairnum)
	PAIRPERCENTS.append(pairperc)
	FWDNUMS.append(fwdnum)
	FWDPERCENTS.append(fwdperc)
	REVNUMS.append(revnum)
	REVPERCENTS.append(revperc)
	DROPNUMS.append(dropnum)
	DROPPERCENTS.append(dropperc)

# Create dataframe with values from lists

df_trimtable = pd.DataFrame({
	'SampleID':SAMPLEIDS,
	'Raw_paired_reads':INPUTREADS,
	'Both_surviving_reads':PAIRNUMS,
	'Both_surviving_percent':PAIRPERCENTS,
	'Fwdonly_surviving_reads':FWDNUMS,
	'Fwdonly_surviving_percent':FWDPERCENTS,
	'Revonly_surviving_reads':REVNUMS,
	'Revonly_surviving_percent':REVPERCENTS,
	'Dropped_reads':DROPNUMS,
	'Dropped_percent':DROPPERCENTS
	})

df_trimtable.to_csv('trimlogs_summary.txt', sep = "\t", index = False)
