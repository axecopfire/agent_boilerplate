#!/bin/sh

TMP_AI_BRANCH_NAME=$1

cd ..

# Check if the branch already exists
if git show-ref --verify --quiet refs/heads/$TMP_AI_BRANCH_NAME; then
    echo "Branch '$TMP_AI_BRANCH_NAME' already exists. Checking out to the branch."

    git checkout $TMP_AI_BRANCH_NAME
else
    echo "Branch '$TMP_AI_BRANCH_NAME' does not exist. Creating branch."
    git commit -m "Creating tmp branch $TMP_AI_BRANCH_NAME" --allow-empty
    git push
    git checkout -b $TMP_AI_BRANCH_NAME
fi
