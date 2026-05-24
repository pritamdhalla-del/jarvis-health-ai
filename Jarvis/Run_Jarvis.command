#!/bin/bash
# JARVIS Launcher
# Double-click this file to start Jarvis

cd "$(dirname "$0")"
source .venv/bin/activate
python jarvis.py
