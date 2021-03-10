#!/usr/bin/env bash

# envvar_append_or_create
#  $1 = envvar name
#  $2 = string to append
function envvar_append_or_create() {
    if [[ ! -n "${!1+1}" ]]; then
        export ${1}="${2}"
    else
        export ${1}="${!1}:${2}"
    fi
}

# envvar_prepend_or_create
#  $1 = envvar name
#  $2 = string to prepend
function envvar_prepend_or_create() {
    if [[ ! -n "${!1+1}" ]]; then
        export ${1}="${2}"
    else
        export ${1}="${2}:${!1}"
    fi
}

# envvar_set_or_create
#  $1 = envvar name
#  $2 = string to prepend
function envvar_set_or_create() {
    export ${1:?}="${2:?}"
}

# envvar_op
# $1 = operation    (set, append, prepend, unset)
# $2 = arg1         (envvar name)
# $3 = arg2         (envvar value - optional)
function envvar_op() {

    local op=${1:?}
    local arg1=${2:?}
    local arg2=${3}

    if [[ "${op}" == "set" ]]; then
        envvar_set_or_create ${arg1:?} ${arg2:?}
    elif [[ "${op}" == "unset" ]]; then
        unset ${arg1:?}
    elif [[ "${op}" == "append" ]]; then
        envvar_append_or_create ${arg1} ${arg2:?}
    elif [[ "${op}" == "prepend" ]]; then
        envvar_prepend_or_create ${arg1} ${arg2:?}
    else
        echo -e "!! ERROR (BASH): Unknown operation: ${op}"
    fi
}

envvar_op set FOO bar
envvar_op append FOO baz
envvar_op prepend FOO foo
envvar_op set BAR foo
envvar_op unset FOO
module purge
module use setenvironment/unittests/modulefiles
module load gcc/4.8.4
module load boost/1.10.1
module load gcc/4.8.4
module unload boost
module swap gcc gcc/7.3.0


