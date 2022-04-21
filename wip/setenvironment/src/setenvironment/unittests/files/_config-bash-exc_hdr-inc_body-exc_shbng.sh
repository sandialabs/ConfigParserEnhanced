# -------------------------------------------------
#   S E T E N V I R O N M E N T   C O M M A N D S
# -------------------------------------------------
envvar_op set "FOO" "bar"
envvar_op append "FOO" "baz"
envvar_op prepend "FOO" "foo"
envvar_op set "BAR" "foo"
envvar_op remove_substr "FOO" "bar"
envvar_op unset "FOO"
module purge
module use src/setenvironment/unittests/modulefiles
module load gcc/4.8.4
module load boost/1.10.1
module load gcc/4.8.4
module unload boost
module swap gcc gcc/7.3.0


