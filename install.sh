#!/usr/bin/env bash
set -e

if [ "$(id -u)" != "0" ]; then
	echo "Permission denied, run script with \"sudo\"."
	exit 1
fi

TAB="\r\t"
FIFT_SOURCES=''
LITE_CLIENT_SOURCES=''
VALIDATOR_ENGINE_SOURCES=''

NODE_CONTROL_SOURCES=''


function get_ton_global_config() {
  echo -e "Processing operation: ${current_step}/${operation_steps}
  ${TAB}Getting TON global config."
  CONFIGURATION=$(curl -fsSL https://ton-blockchain.github.io/global.config.json)
  echo "Successfully downloaded TON global config."
}

function check_ton_sources_installed() {
  echo -e "${TAB}Checking TON sources are installed."
}

function install_lite_server() {
  echo -e "Processing operation: ${current_step}/${operation_steps}
  ${TAB}Installing lite server"
  check_ton_sources_installed
}

function install_tonlib() {
  echo -e "Processing operation: ${current_step}/${operation_steps}
  ${TAB}Installing tonlib"
}

operations=(
  get_ton_global_config
  install_lite_server
  install_tonlib
)
operation_steps=$(expr ${#operations[@]})

for index in ${!operations[*]}
  do
    callable=${operations[$index]}
    current_step=$(expr ${index} + 1)
    $callable
  done
