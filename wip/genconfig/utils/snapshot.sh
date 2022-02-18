#!/bin/bash -el
# Usage: snapshot.sh /path/to/GenConfig /path/to/Trilinos/package/name RELEASE_TAG
gc_path=$1
tr_path=$2
release_tag=$3

repo_prefix=git@internal.gitlab.server:trilinos-devops-consolidation/code

repos="GenConfig ConfigParserEnhanced SetEnvironment DetermineSystem KeywordParser loadenv SetProgramOptions"

# A) Archive repos at $release_tag and expand archives in $tr_path
pushd $gc_path
for repo in $repos; do
  cmd="git archive --format=tar --remote=${repo_prefix}/${repo}.git --prefix=${repo}/ $release_tag | (cd $tr_path && tar xf -)"
  echo "$cmd"
  eval $cmd
  pushd $tr_path
  git add -f $repo
  popd
done
popd

# B) Rename loadenv
pushd $tr_path
mv -f loadenv/ LoadEnv/
git add -f LoadEnv
popd

# C) Setup GenConfig symlinks
pushd $tr_path/GenConfig
ln -sf ../SetEnvironment/src/setenvironment/ .; git add -f setenvironment
ln -sf ../ConfigParserEnhanced/src/configparserenhanced/ .; git add -f configparserenhanced
ln -sf ../DetermineSystem/determinesystem/ .; git add -f determinesystem
ln -sf ../KeywordParser/keywordparser/ .; git add -f keywordparser
ln -sf ../LoadEnv .; git add -f LoadEnv
ln -sf ../SetProgramOptions/src/setprogramoptions .; git add -f setprogramoptions
popd

# D) Setup LoadEnv symlinks
pushd $tr_path/LoadEnv
ln -sf ../SetEnvironment/src/setenvironment/ .; git add -f setenvironment
ln -sf ../ConfigParserEnhanced/src/configparserenhanced/ .; git add -f configparserenhanced
ln -sf ../DetermineSystem/determinesystem/ .; git add -f determinesystem
ln -sf ../KeywordParser/keywordparser/ .; git add -f keywordparser
popd

# E) Remove unnecessary files
rm -f $tr_path/GenConfig/install-reqs.sh
rm -r $tr_path/LoadEnv/install_reqs.sh

# F) Commit changes
echo "Generated by \"$(basename $0 $@ | tr '\n' ' ')\"" > $tr_path/snapshot_${release_tag}.out
pushd $tr_path
git add -f snapshot_${release_tag}.out
git commit -m "Snapshot of GenConfig@${release_tag}"
popd