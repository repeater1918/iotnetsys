#!/bin/bash

filename="cooja_packets.testlog"

while read line; do
  echo "$line"
done < "$filename"

echo "end of file"
