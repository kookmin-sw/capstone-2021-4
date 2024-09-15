#!/bin/bash
cd app
# MacOS일 때 만
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
rq worker