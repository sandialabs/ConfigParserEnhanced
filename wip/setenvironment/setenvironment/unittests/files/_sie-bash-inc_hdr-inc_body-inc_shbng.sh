#!/usr/bin/env bash
# ---------------------------------------------------
#   S E T E N V I R O N M E N T   F U N C T I O N S
# ---------------------------------------------------


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

# envvar_assert_not_empty
# $1 = envvar name
# $2 = optional error message
function envvar_assert_not_empty() {
    local envvar=${1}
    local message=${2}
    if [[ -z "${!envvar}" ]]; then
        if [[ -z "${message}" ]]; then
            echo "ERROR: ${envvar} is empty or not set"
        else
            echo "${message}"
        fi
        exit 1
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
#  $2 = string to set the value to.
function envvar_set_or_create() {
    export ${1:?}="${2}"
}

# envvar_set_if_empty
# Param1: Envvar name
# Param2: Envvar value
function envvar_set_if_empty() {
    local ENVVAR_NAME=${1:?}
    local ENVVAR_VALUE=${2}
    if [[ -z "${!ENVVAR_NAME}" ]]; then
        export ${ENVVAR_NAME}="${ENVVAR_VALUE}"
    fi
}

# envvar_remove_substr
# $1 = envvar name
# $2 = substring to remove
function envvar_remove_substr() {
    local envvar=${1:?}
    local substr=${2:?}
    #echo "envvar   : ${envvar}" > /dev/stdout
    #echo "to_remove: ${substr}" > /dev/stdout
    if [[ "${substr}" == *"#"* ]]; then
        printf "%s\n" "ERROR: $FUNCNAME: "$substr" contains a '#' which is invalid." 2>&1
        return
    fi
    if [ ! -z ${1:?} ]; then
        export ${envvar}=$(echo ${!envvar} | sed s#${substr}##g)
    fi
}

# envvar_remove_path_entry
# $1 = A path style envvar name
# $2 = Entry to remove from the path.
function envvar_remove_path_entry() {
    local envvar=${1:?}
    local to_remove=${2:?}
    local new_value=${!envvar}
    #echo -e "envvar = ${envvar}" > /dev/stdout
    #echo -e "to_remove = ${to_remove}" > /dev/stdout
    #echo -e "new_value = ${new_value}" > /dev/stdout
    if [ ! -z ${envvar} ]; then
        new_value=:${new_value}:
        new_value=${new_value//:${to_remove}:/:}
        new_value=${new_value#:1}
        new_value=${new_value%:1}
        export ${envvar}=${new_value}
    fi
}

# envvar_op
# $1 = operation    (set, append, prepend, unset)
# $2 = arg1         (envvar name)
# $3 = arg2         (envvar value - optional)
function envvar_op() {
    local op=${1:?}
    local arg1=${2:?}
    local arg2=${3}
    if [[ "${op:?}" == "set" ]]; then
        envvar_set_or_create ${arg1:?} "${arg2}"
    elif [[ "${op:?}" == "unset" ]]; then
        unset ${arg1:?}
    elif [[ "${op:?}" == "append" ]]; then
        envvar_append_or_create ${arg1:?} "${arg2:?}"
    elif [[ "${op:?}" == "prepend" ]]; then
        envvar_prepend_or_create ${arg1:?} "${arg2:?}"
    elif [[ "${op:?}" == "remove_substr" ]]; then
        envvar_remove_substr ${arg1:?} "${arg2:?}"
    elif [[ "${op:?}" == "remove_path_entry" ]]; then
        envvar_remove_path_entry ${arg1:?} "${arg2:?}"
    elif [[ "${op:?}" == "find_in_path" ]]; then
        envvar_set_or_create ${arg1:?} "$(which ${arg2:?})"
    elif [[ "${op:?}" == "assert_not_empty" ]]; then
        envvar_assert_not_empty "${arg1:?}" "${arg2}"
    elif [[ "${op:?}" == "set_if_empty" ]]; then
        envvar_set_if_empty "${arg1:?}" "${arg2}"
    else
        echo -e "!! ERROR (BASH): Unknown operation: ${op:?}"
    fi
}


# -------------------------------------------------
#   S E T E N V I R O N M E N T   C O M M A N D S
# -------------------------------------------------
envvar_op unset FOO_VAR
envvar_op unset BAR_VAR
envvar_op unset BAZ_VAR
envvar_op unset BIF_VAR
envvar_op set FOO_VAR FOO_VAL
envvar_op set BAR_VAR ""
envvar_op set_if_empty FOO_VAR BAR_VAL
envvar_op set_if_empty BAR_VAR BAR_VAL
envvar_op set_if_empty BAZ_VAR BAZ_VAL
envvar_op set_if_empty BIF_VAR ""


