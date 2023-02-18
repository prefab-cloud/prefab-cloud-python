#!/usr/bin/env bash
cp ../prefab-cloud/prefab.proto .
protoc -I=. --python_out=. ./prefab.proto

