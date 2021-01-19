#!/bin/bash

source /usr/local/bin/thisroot.sh
bash /usr/local/bin/NanoAODTools/standalone/env_standalone.sh build
source /usr/local/bin/NanoAODTools/standalone/env_standalone.sh
python3 tree_skimmer_ssWW_wFakes.py $1 $2 $3 $4
