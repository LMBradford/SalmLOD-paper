import pandas as pd

# Run in the Summaries directory

# Read in other summary tables
df_trimtable = pd.read_csv('trimlogs_summary.txt', sep='\t')
df_host = pd.read_csv('hostcheck_summary.txt', sep='\t')
df_kr2rep = pd.read_csv('kr2rep_summary.txt', sep='\t')
df_kr2salm = pd.read_csv('kr2salmhits_summary.txt', sep='\t')
df_SSRsalm = pd.read_csv('ssr-salmhits_summary.txt', sep='\t')

# Merge 1: selected Trimlog columns + hostcheck
df_merg1 = pd.merge(df_trimtable[[
	'SampleID',
	'Raw_paired_reads',
	'Both_surviving_percent',
	'Dropped_reads',
	'Dropped_percent']],
	df_host, on='SampleID', how='left')

# Calculate reads into Kraken 2 analysis
df_merg1['Reads_into_Kr2'] = df_merg1['Raw_paired_reads'] - df_merg1['Dropped_reads'] - df_merg1['Num_hostreads']

# Merge 2: 
DFS_merge2 = [df_merg1, df_kr2rep, df_kr2salm, df_SSRsalm]

df = pd.concat(DFS_merge2, axis=1) 
df = df.loc[:,~df.columns.duplicated()] #Remove duplicate Sample Name columns

#print(df)
df.to_csv('results_test.tsv', sep = "\t", index = False)
