from utils import Utils
import uuid


"""
1st iteration:
    Create main ai branch
    Make a PR to main branch

Create tmp ai branch off it and change to that one
git commit: code_action + Summary + new code_insight = did_it_hurt?
git commit: log summary, code_insight, hurt
push to tmp ai branch
if hurt:
    Start iteration 2 with Summary and new code_insight
    cherry-pick log summary, code_insight, hurt to main ai branch
    change to main ai branch
else:
    Push changes to main ai branch
"""

"""
1st iteration:
    Create main ai branch
    Make a PR to main branch

Create tmp ai branch off it and change to that one
git commit: code_action + Summary + new code_insight = did_it_hurt?
git commit: log summary, code_insight, hurt
push to tmp ai branch
if hurt:
    Start iteration 2 with Summary and new code_insight
    cherry-pick log summary, code_insight, hurt to main ai branch
    change to main ai branch
else:
    Push changes to main ai branch
"""


class LocalGitSubProcesses:
    def __init__(self):
        self.u = Utils()

    def init_main_ai_branch(self, main_ai_branch_name):

        self.main_ai_branch = main_ai_branch_name

        # Check to see if branch exists
        res = self.u.run_subprocess(
            f"./git/init_main_ai_branch.sh {main_ai_branch_name}"
        )

        print(res[0])

    def create_tmp_ai_branch(self, tmp_ai_branch_name):
        res = self.u.run_subprocess(
            f"./git/create_tmp_ai_branch.sh {tmp_ai_branch_name}"
        )

        print(res[0])

        return tmp_ai_branch_name

    def commit_code_action(self, commit_message, helpful):
        res = self.u.run_subprocess(
            f"./git/commit_code_action.sh {commit_message} {helpful}"
        )

        return res[0]
