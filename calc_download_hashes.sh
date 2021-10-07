#!/bin/sh

for i in downloads/*; do
    tar c "$i" | sha256sum
done
