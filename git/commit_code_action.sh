#!/bin/sh

COMMIT_MSG=$1
HELPFUL=$2

cd ..

git add .

git commit -m $COMMIT_MSG

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push -u origin $CURRENT_BRANCH

# Get the tmp branch's hash of the most recent commit
RECENT_COMMIT_HASH=$(git rev-parse HEAD)

# Return back to main_ai branch
git checkout -

# If the content was marked as helpful then update the main_ai branch
if [ "$HELPFUL" = "True" ]; then
    git cherry-pick $RECENT_COMMIT_HASH
    git push
fi