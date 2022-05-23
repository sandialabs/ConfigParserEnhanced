#!/usr/bin/env python3
########################################################################################################################
# Quick CLI script to pull out the job names from a autotester config file
########################################################################################################################

import configparser
import sys
import re

cfg = configparser.ConfigParser(strict=False)
cfg.read(sys.argv[1])
token=sys.argv[2]

for s in cfg:
    if s.startswith("JENKINS_JOBS_FROM_SERVER_JENKINS_TRILINOS_JAAS_FOR_GROUP_TRILINOS"):
        for i in cfg[s]:
            if re.match(token.lower(), i) != None:
                print(cfg[s][i])