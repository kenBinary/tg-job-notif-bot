#!/bin/bash

echo "Starting dev tables cleanup and recreation..."

echo "Step 1: Removing existing tables..."
python -m scripts.table_cleanup --dev

echo "Step 2: Creating fresh tables..."
python -m scripts.create_tables --dev

echo "Dev tables cleanup and recreation complete!"