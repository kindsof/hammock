#! /usr/bin/env bash

ab -n 50000 "http://localhost:8000/?path=$PWD/files/resources/"
