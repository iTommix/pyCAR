#!/bin/bash
text="'$*'"
#file=/home/pyCAR/lastspeak.txt
espeak -v mb/mb-de5 -a 70 -s 150 "$text"
#echo "$text" > "$file"
