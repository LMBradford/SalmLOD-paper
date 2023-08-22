#NOTES##############################################################################################
#No conda on Compute Canada
##Software loaded as modules in SLURM file instead

# This workflow is submitted as three separate jobs.
# Step 1 must be complete before step 2 is submitted
# All steps use the same config files

#Steps are separated for more efficient use of compute Canada resources

#CONFIG FILE ###########################################################################################################################################################

#Define the config yaml file in the command line

#VARIABLE SETUP ########################################################################################################################################################

#Import packages for file name management
import glob
#These imports let me use wildcards to take in file names and maintain the name info throughout the workflow

import os
#needed for pointing to location of kr2bac in rules kr2pair and kr2unpair

envvars:
  "SLURM_TMPDIR"
#Will be used in rule cp_db

#Detect wildcards from input files names
#Names must be fixed up with renamefastq.py
#Update data in config file to reflect name and filename info for project
#Project ID (ex. FS for feedspike) and sample name are used for all output file names
filename = config['pathtoinput'] + config['projID'] + "-" + config['seqtype'] + "_{name}_R1.fastq.gz"

NAME, = glob_wildcards(filename)

print(NAME)

PROJID = config['projID']


#CATCH-ALL RULE ###################################################################################################################################################

rule all:
  #List all the final output files expected here.
  input:
    expand("Trim/{projID}_{name}_unpaired.fq.gz", name=NAME, projID = PROJID),
  

#TRIMMING STEP ################################################################################################################################################

#Trim for quality using Trimmomatic
rule trim:
  input:
    fwd = config['pathtoinput'] + config['projID'] + "-" + config['seqtype'] + "_{name}_R1.fastq.gz",
    rev = config['pathtoinput'] + config['projID'] + "-" + config['seqtype'] + "_{name}_R2.fastq.gz"
  output:
    fwdp = "Trim/" + config['projID'] + "_{name}_R1.P.fq.gz",
    fwdu = "Trim/" + config['projID'] + "_{name}_R1.U.fq.gz",
    revp = "Trim/" + config['projID'] + "_{name}_R2.P.fq.gz",
    revu = "Trim/" + config['projID'] + "_{name}_R2.U.fq.gz",
    log = "Trimlogs/" + config['projID'] + "_{name}_trimlog.txt"
  shell:
    "java -jar $EBROOTTRIMMOMATIC/trimmomatic-0.39.jar PE -summary {output.log} \
    {input.fwd} {input.rev} {output.fwdp} {output.fwdu} {output.revp} {output.revu} \
    SLIDINGWINDOW:4:20 MINLEN:36"
        
#Concatenate trimmed unpaired sequences together
rule cat_unpaired:
  input:
    unpaired_R1 = "Trim/" + config['projID'] + "_{name}_R1.U.fq.gz",
    unpaired_R2 = "Trim/" + config['projID'] + "_{name}_R2.U.fq.gz"
  output:
    "Trim/" + config['projID'] + "_{name}_unpaired.fq.gz"
  shell:
    "cat {input.unpaired_R1} {input.unpaired_R2} > {output}"
