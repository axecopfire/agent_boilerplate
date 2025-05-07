#!/bin/bash


branches=(
  "tmp_ai_33152f78-49cc-4be2-b155-29a288c4d6d1"
  "tmp_ai_33b9c591-7b1d-4b62-a1f6-872f8166b8be"
  "tmp_ai_391b5b59-797a-4836-a13f-75878b71508c"
  "tmp_ai_4b291918-a9cd-4146-a1f0-06f3d6c25e8b"
  "tmp_ai_524b30b3-d2db-4722-b823-adbeba001417"
  "tmp_ai_53017891-720d-4d4b-ae28-4adb731c51de"
  "tmp_ai_54a68b6a-d3e0-405a-a74c-366e24a7bac5"
  "tmp_ai_58338968-e01b-4d4c-a6f9-bb234f40152e"
  "tmp_ai_5e74a1d1-d702-48d2-a80d-ef496a651551"
  "tmp_ai_6bb337bc-3062-4e02-bca2-61ad012cb51f"
  "tmp_ai_6e8be4da-1dea-4799-8fbe-108cb72469d5"
  "tmp_ai_7ed1fece-01bc-4b0c-9dab-83bd8bfbb801"
  "tmp_ai_8de6044d-ccd2-44b2-b4cf-1e38ae60bc11"
  "tmp_ai_90571dbb-d90d-4d85-83ee-fc08802ba967"
  "tmp_ai_9081dfcf-f00d-4dd8-8108-8bf34873abd2"
  "tmp_ai_933e0600-6e8f-4bae-afdd-cf363b134bae"
  "tmp_ai_99357eb5-89df-418f-a66a-c211e4b4a1ff"
  "tmp_ai_9935a555-11e3-4c9f-a9d5-4ecc3a31875c"
  "tmp_ai_c685e1c1-01db-4a7f-8050-69248c327913"
  "tmp_ai_ce8581b4-d331-427c-98ea-b317f2d2aeda"
  "tmp_ai_d372e763-ecc3-41b7-8354-7bffcf3de701"
  "tmp_ai_d5362d86-d75e-4857-b178-d7ebcb5320f2"
  "tmp_ai_e85461d3-f0d6-410a-9b25-30ac27b0df53"
)

# $ git push <remote_name> --delete <branch_name>

for branch in "${branches[@]}"; do
    echo "Deleting branch: $branch"
    # git branch -D $branch
    
    git push origin --delete $branch
done

# For local listing
# git branch -l

# For remote listing
git branch -r
