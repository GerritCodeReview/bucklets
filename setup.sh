#!/bin/bash
set -e

for file in buckversion watchmanconfig; do
  rm -f .$file
  ln -s bucklets/$file .$file
done

