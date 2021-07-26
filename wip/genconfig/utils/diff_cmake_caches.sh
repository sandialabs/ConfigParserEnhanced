#!/bin/bash

#path_cur="/scratch/eharvey/TRILINOS-CONSOLIDATION.base/Trilinos/build-gcc8.3.0"
#path_pr="/scratch/trilinos/jenkins/ascic141/workspace/trilinos-folder/Trilinos_pullrequest_gcc_8.3.0/pull_request_test"

#path_cur="/scratch/trilinos/jenkins/ascic142/workspace/trilinos-folder/Trilinos_pullrequest_rhel7_sems-gnu-7.2.0-openmpi-1.10.1-serial_release-debug_shared_no-kokkos-arch_no-asan_no-complex_no-fpic_no-mpi_no-pt_no-rdc_trilinos-pr/pull_request_test"
#path_cur="/scratch/eharvey/TRILINOS-CONSOLIDATION.base/Trilinos/build"
#path_pr="/scratch/trilinos/jenkins/ascic143/workspace/trilinos-folder/Trilinos_pullrequest_gcc_7.2.0_serial/pull_request_test"

#path_cur="/scratch/eharvey/TRILINOS-CONSOLIDATION.base/Trilinos/build"
#path_pr="/scratch/trilinos/jenkins/ascic166/workspace/trilinos-folder/Trilinos_pullrequest_clang_10.0.0/pull_request_test"

path_cur="/scratch/eharvey/TRILINOS-CONSOLIDATION.base/Trilinos/build"
path_pr="/scratch/trilinos/jenkins/ascic158/workspace/trilinos-folder/Trilinos_pullrequest_intel_17.0.1/pull_request_test"

if [[ ! "$@" == *"--include-cmake-var-type"* ]]; then
    echo "WARNING: Ignoring cmake variable types; to include, run this script with --include-cmake-var-type"
fi

echo ""
echo "WARNING: removing \"path_cur=$path_cur\" from $1 temp file"
echo "WARNING: if \"path_cur\" is wrong, please modify it at the top of $0."

echo ""
echo "WARNING: removing \"path_pr=$path_pr\" from $2 temp file"
echo "WARNING: if \"path_pr\" is wrong, please modify it at the top of $0."

egrep -v '#|//' $1 | tr -s '\n' | sed "s|$path_cur||g" > cur
egrep -v '#|//' $2 | tr -s '\n' | sed "s|$path_pr||g" > pr

echo ""
echo "STATUS: Searching for all cmake vars in $2 that do not match cmake vars in $1..."

echo "" > cur_missing
echo "" > cur_mismatch
matches=0
total=0
mismatched=0
missing=0
while IFS= read -r <&4 pr_line; do
    if [ $(echo $pr_line | wc -c) -lt 2 ]; then
	continue
    fi
    var_name=""
    if [[ "$@" == *"--include-cmake-var-type"* ]]; then
	var_name=$(echo $pr_line | awk -F ':' '{print $1":"$2}' | awk -F '=' '{print $1}')
    else
	var_name=$(echo $pr_line | awk -F ':' '{print $1":"}' | awk -F '=' '{print $1}')
    fi

    var_found=$(cat cur | grep ^${var_name})
    grep_ret=$?
    if [[ ! "$@" == *"--include-cmake-var-type"* ]]; then
	if [[ ! "$var_found" == *":INTERNAL="* ]]; then
	   var_found=$(echo $var_found | sed 's|\:.*=|=|g')
	fi

	if [[ ! "$pr_line" == *":INTERNAL="* ]]; then
	   pr_line=$(echo $pr_line | sed 's|\:.*=|=|g')
	fi
    fi

    if [[ $grep_ret -ne 0 ]]; then
    	echo "$1 missing $var_name -> $pr_line" >> cur_missing
	missing=$(($missing+1))
    else
    	if [ "$var_found" == "$pr_line" ]; then
	    matches=$(($matches+1))
    	else
	    # TODO: highlight diff in color
    	    echo "$1 mismatch $var_found -> $pr_line" >> cur_mismatch
	    mismatched=$(($mismatched+1))
    	fi
    fi
    total=$(($total+1))
done 4< "pr"

echo ""
echo "STATUS: Done searching."
echo ""
echo "matched: $matches/$total, mismatched: $mismatched/$total, missing: $missing/$total"
echo ""
echo "**opening \"grep -v INTERNAL cur_mismatch\", for all non-internal mismatched cmake vars that are in $2 but not in $1**"
echo "PRESS 'q' to quit"
grep -v INTERNAL cur_mismatch | less

echo "**opening \"grep -v INTERNAL cur_missing\", for all non-internal missing cmake vars that are in $2 but not in $1**"
echo "PRESS 'q' to quit"
grep -v INTERNAL cur_missing | less
