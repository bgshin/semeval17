#!/bin/bash

# for f in *.tsv
# do
#     echo $f
#     cat $f | wc -l
# done


# for f in *.tsv
# do
#     echo $f
#     cat $f | grep "Not Available" | wc -l
# done
for f in *.clean
do
    echo $f
    cat $f | wc -l
done
