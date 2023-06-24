#!/usr/bin/env bash

# https://buf.build/docs/installation

cp ../prefab-cloud/prefab.proto .
buf generate
