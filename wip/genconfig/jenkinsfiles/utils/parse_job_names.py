#!/usr/bin/env python3
########################################################################################################################
# Quick CLI script to pull out the job names from a autotester config file
########################################################################################################################

import configparser
import sys

cfg = configparser.ConfigParser(strict=False)
cfg.read(sys.argv[1])

for s in cfg:
    if s.startswith("JENKINS_JOBS_FROM_SERVER_JENKINS"):
        for i in cfg[s]:
            if i.startswith("job"):
                print(cfg[s][i])