#!/bin/sh

MAIN_AI_BRANCH_NAME=$1
cd ..

# Check if the branch already exists
if git show-ref --verify --quiet refs/heads/$MAIN_AI_BRANCH_NAME; then
    echo "Branch '$MAIN_AI_BRANCH_NAME' already exists. Checking out to the branch."
    git checkout $MAIN_AI_BRANCH_NAME
else
    echo "Branch '$MAIN_AI_BRANCH_NAME' does not exist. Creating making init commit."

    git checkout -b $MAIN_AI_BRANCH_NAME

    git commit -m 'Initial ai commit' --allow-empty

    git push -u origin $MAIN_AI_BRANCH_NAME
fi
