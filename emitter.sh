#!/bin/bash

filename="cooja.testlog"

while read line; do
  echo "$line"
done < "$filename"

echo "end of file"
