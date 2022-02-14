#!/bin/bash

./install-reqs.sh
rm -rf utils/supporting_files/srn-ini-files
git clone git@cee-gitlab.sandia.gov:trilinos-project/srn-ini-files.git utils/supporting_files/srn-ini-files

# Set to 1 to see verbose output
verbose=1
# Check for keywords that should not be released
kwl=$(cat utils/supporting_files/srn-ini-files/trilinos/sensitive_keywords.txt | tr '\n' '|')
base=$(pwd)

# Check GenConfig
check="git grep -q -E \"$kwl\""

function do_check() {
  eval ${check}
  ret=$?

  if [ $ret -eq 0 ]; then
    tput blink && tput setaf 1 && echo "FAIL: Sensitive keywords found in $PWD" && tput sgr0
    if [ $verbose -eq 1 ]; then
      git grep -c -E $kwl > found_in_files.txt
      printf "Sensitive keywords:\n\t"
      printf $(echo $kwl | sed 's/|/\\n\\t/g')
      printf "\n\nFound in:\n\t"
      printf $(cat found_in_files.txt | tr '\n' '|' | sed 's/|/\\n\\t/g')
    fi
  else
    tput setaf 2 && echo "PASS: Nothing sensitive found in $PWD" && tput sgr0
  fi
}

for dep in $(echo $PWD; ls deps); do
  cd $dep
  do_check
  cd -
done