#!/usr/bin/env bash

INTERFACE="wlp4s0"
AP1="18:e8:29:c6:0c:0f"
AP2="18:e8:29:10:b0:8b"
AP3="18:e8:29:c6:0f:3f"
AP4="74:83:c2:96:ee:27"
echo "-----------------------------------------"  >> log_ap.txt
echo "-----------------------------------------"  >> log_ap.txt
echo "-----------------------------------------"  >> log_ap.txt
while [ 1 ];
do CONNECTED_AP=$(iwconfig $INTERFACE |grep "Access Point" | cut -d ':' -f 4-9 | cut -c 2-);

DIFFERENCE1=$(diff -w  <(echo "$CONNECTED_AP") <(echo "$AP1"));
DIFFERENCE2=$(diff -w  <(echo "$CONNECTED_AP") <(echo "$AP2"));
DIFFERENCE3=$(diff -w  <(echo "$CONNECTED_AP") <(echo "$AP3"));
DIFFERENCE4=$(diff -w  <(echo "$CONNECTED_AP") <(echo "$AP4"));

WIFI_QUALITY=$(iwconfig $INTERFACE | sed '6q;d')

now=$(date +"%T")
if [ -z "$DIFFERENCE1" ]
then
        echo "AP1:" $now >> log_ap.txt
        echo $WIFI_QUALITY >> log_ap.txt
elif [ -z "$DIFFERENCE2" ]
then
        echo "AP2:" $now >> log_ap.txt
        echo $WIFI_QUALITY >> log_ap.txt
elif [ -z "$DIFFERENCE3" ]
then
        echo "AP3:" $now >> log_ap.txt
        echo $WIFI_QUALITY >> log_ap.txt
else
        echo "AP4:" $now >> log_ap.txt
        echo $WIFI_QUALITY >> log_ap.txt
fi
sleep 1;

test $? -gt 128 && break;
done
