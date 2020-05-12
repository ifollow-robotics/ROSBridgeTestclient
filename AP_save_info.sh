#!/usr/bin/env bash

INTERFACE="wlp1s0"
AP1="18:E8:29:FF:F1:39"
AP2="74:83:c2:93:3d:84"
while [ 1 ];
do CONNECTED_AP=$(iwconfig wlp1s0 |grep "Access Point" | cut -d ':' -f 4-9 | cut -c 2-);

DIFFERENCE=$(diff -w  <(echo "$CONNECTED_AP") <(echo "$AP1"));
now=$(date +"%T")
if [ -z "$DIFFERENCE"]
then
        echo "AP1:" $now >> log_ap.txt
else
        echo "AP2:" $now >> log_ap.txt
fi
sleep 1;

test $? -gt 128 && break;
done
