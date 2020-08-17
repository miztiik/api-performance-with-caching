#!/bin/bash
set -ex
set -o pipefail

# version: 17Aug2020

##################################################
#############     SET GLOBALS     ################
##################################################
UNCACHED_API_LOG="/var/log/miztiik-load-generator-uncached.log"
CACHED_API_LOG="/var/log/miztiik-load-generator-cached.log"
UNCACHED_API_URL="https://x60fl6u8f7.execute-api.us-east-1.amazonaws.com/miztiik/uncached/movie"
CACHED_API_URL="https://srcjub0asd.execute-api.us-east-1.amazonaws.com/miztiik/cached/movie"
TOTAL_REQUESTS=2000
for i in $(seq $TOTAL_REQUESTS)
do
    sleep 0.1
    RANDOM_M_ID=$(( ${RANDOM} % 11 ))
    curl -o /dev/null -s -w '{"uncached_latency": "%{time_starttransfer}"} \n' -X GET "${UNCACHED_API_URL}/${RANDOM_M_ID}" >> "${UNCACHED_API_LOG}"
    curl -o /dev/null -s -w '{"cached_latency": "%{time_starttransfer}"} \n' -X GET "${CACHED_API_URL}/${RANDOM_M_ID}" >> "${CACHED_API_LOG}"

done
sleep 35
TOTAL_REQUESTS=2000
for i in $(seq $TOTAL_REQUESTS)
do
    sleep 0.2
    RANDOM_M_ID=$(( ${RANDOM} % 11 ))
    curl -o /dev/null -s -w '{"uncached_latency": "%{time_starttransfer}"} \n' -X GET "${UNCACHED_API_URL}/${RANDOM_M_ID}" >> "${UNCACHED_API_LOG}"
    curl -o /dev/null -s -w '{"cached_latency": "%{time_starttransfer}"} \n' -X GET "${CACHED_API_URL}/${RANDOM_M_ID}" >> "${CACHED_API_LOG}"

done
sleep 35
TOTAL_REQUESTS=2000
for i in $(seq $TOTAL_REQUESTS)
do
    sleep 0.3
    RANDOM_M_ID=$(( ${RANDOM} % 11 ))
    curl -o /dev/null -s -w '{"uncached_latency": "%{time_starttransfer}"} \n' -X GET "${UNCACHED_API_URL}/${RANDOM_M_ID}" >> "${UNCACHED_API_LOG}"
    curl -o /dev/null -s -w '{"cached_latency": "%{time_starttransfer}"} \n' -X GET "${CACHED_API_URL}/${RANDOM_M_ID}" >> "${CACHED_API_LOG}"

done
sleep 35
TOTAL_REQUESTS=2000
for i in $(seq $TOTAL_REQUESTS)
do
    sleep 0.4
    RANDOM_M_ID=$(( ${RANDOM} % 11 ))
    curl -o /dev/null -s -w '{"uncached_latency": "%{time_starttransfer}"} \n' -X GET "${UNCACHED_API_URL}/${RANDOM_M_ID}" >> "${UNCACHED_API_LOG}"
    curl -o /dev/null -s -w '{"cached_latency": "%{time_starttransfer}"} \n' -X GET "${CACHED_API_URL}/${RANDOM_M_ID}" >> "${CACHED_API_LOG}"

done
sleep 31
TOTAL_REQUESTS=2000
for i in $(seq $TOTAL_REQUESTS)
do
    sleep 0.5
    RANDOM_M_ID=$(( ${RANDOM} % 11 ))
    curl -o /dev/null -s -w '{"uncached_latency": "%{time_starttransfer}"} \n' -X GET "${UNCACHED_API_URL}/${RANDOM_M_ID}" >> "${UNCACHED_API_LOG}"
    curl -o /dev/null -s -w '{"cached_latency": "%{time_starttransfer}"} \n' -X GET "${CACHED_API_URL}/${RANDOM_M_ID}" >> "${CACHED_API_LOG}"

done

