#!/usr/bin/env bash
set -e

if [ "$(id -u)" != "0" ]; then
	echo "Permission denied, run script with \"sudo\"."
	exit 1
fi

TABULATION="\r\t"

function get_ton_global_config() {
  echo -e "Processing operation: ${current_step}/${operation_steps}
  ${TABULATION}Getting TON global config."
  CONFIGURATION=$(curl -fsSL https://ton-blockchain.github.io/global.config.json)
  echo "Successfully downloaded TON global config"
}

function install_lite_server() {
  echo -e "Processing operation: ${current_step}/${operation_steps}
  ${TABULATION}Installing lite server"
}

function install_tonlib() {
  echo -e "Processing operation: ${current_step}/${operation_steps}
  ${TABULATION}Installing tonlib"
}

operations=(
  get_ton_global_config
  install_lite_server
  install_tonlib
)
operation_steps=$(expr ${#operations[@]} + 1)

for index in ${!operations[*]}
  do
    callable=${operations[$index]}
    current_step=$(expr ${index} + 1)
    $callable
  done
