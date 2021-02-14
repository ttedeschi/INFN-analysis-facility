#!/bin/bash

bash /usr/local/bin/NanoAODTools/standalone/env_standalone.sh build
source /usr/local/bin/NanoAODTools/standalone/env_standalone.sh
source /usr/local/bin/thisroot.sh
python3 tree_skimmer_ssWW_wFakes.py $1 $2 $3 $4
