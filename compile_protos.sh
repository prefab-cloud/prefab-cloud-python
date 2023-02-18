#!/usr/bin/env bash
cp ../prefab-cloud/prefab.proto .
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./prefab.proto
