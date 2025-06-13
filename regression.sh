#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

rm -rf build/tb_test

for x in $(seq 100); do
	seed=$RANDOM
	make tb/npu/tb_test enable=opt,rand seed=$seed
done
