from library.agents.base_agent import Agent
import asyncio
from executor.docker_runner import docker_executor
from pydantic import BaseModel
from .coding_strategy import GenerateCodingStrategy
from utils.logging_config import use_console_logger, use_file_logger, logger
import json
from utils.utils import Utils


from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fix the code so it builds and runs correctly
# Build a feature

# Test the feature
# Make the tests pass
# scale the feature's functionality
# If you scale too quickly it breaks the AI not knowing where to start. It needs to try a few things before it settles on the right strategy. Will need to do cleanup task
#


class Flow:
    def __init__(self, goal, language, root_dir):
        use_console_logger()
        self.goal = goal
        self.language = language
        self.root_dir = root_dir
        self.strategy = GenerateCodingStrategy(
            goal=goal, root_dir=root_dir, language=language
        )
        self.utils = Utils(root_dir)

        if language == "Kotlin":
            docs_folder = "docs/kotlin_logs"
        elif language == "Python":
            docs_folder = "docs/py_demo_logs"

        self.kb_path = os.path.join(docs_folder, "ai_kb.txt")
        self.ai_log_path = os.path.join(docs_folder, "ai_log.txt")
        self.ai_suggestion_path = os.path.join(docs_folder, "ai_suggestion_log.txt")
        self.manual_kb_path = os.path.join(docs_folder, "manual_kb.txt")

    def get_last_suggestion(self):
        with open(self.ai_suggestion_path, "r") as f:
            lines = f.readlines()
            goal_read = lines[-1] if lines else ""
        return goal_read

    def read_logs(self):
        with open(self.kb_path, "r") as f:
            kb_read = f.read()

        with open(self.ai_log_path, "r") as f:
            log_read = f.read()

        with open(self.manual_kb_path, "r") as f:
            manual_kb_read = f.read()

        return {
            "kb_read": kb_read,
            "log_read": log_read,
            "manual_kb_read": manual_kb_read,
        }

    def write_logs(self, kb_content, summary, suggestion):
        with open(self.kb_path, "w") as f:
            f.write(kb_content)

        with open(self.ai_log_path, "a") as f:
            f.write(f"\n{summary}")

        with open(self.ai_suggestion_path, "a") as f:
            f.write(f"\n{suggestion}")

    def run_pytest(self):
        res = self.utils.run_subprocess(f"./executor/run_pytest.sh {self.root_dir}")
        return res[0].replace("\\n", "\n ")

    async def run_docker():

        res = await docker_executor()
        return res["stdout"]

    async def get_insights(self):
        if self.language == "Kotlin":
            insights = await self.run_docker()
        elif self.language == "Python":
            insights = self.run_pytest()

        return insights

    def get_context(self, insights):
        # Strategy was initialized with a goal that lacked insights. Update that goal.
        self.strategy.goal = f"""
        ## Insights
        {insights}

        ## User's goal
        {self.goal}"""

        return self.strategy.get_context()

    def code_action(self, insights, context, log_read, kb_read, suggestion):

        class CodeWriterProposal(BaseModel):
            code: str
            filename: str
            reason: str

        # ## All Previous actions taken by Agent
        # {log_read}

        code_writer = Agent(
            "coder",
            f"""Write code to improve the project. Try to make only 1 code change at a time. Your response will directly overwrite the file with your code. So make sure you add all other contents in the file to your response.  Here is some context to help.

        ## User Story Goal
        {self.goal}

        ## AI Knowledge Base
        {kb_read}

        ## State of the repo
        {context}

        ## Code Result
        {insights}
        """,
        )

        return code_writer(suggestion, CodeWriterProposal)

    def knowledge_base_admin(
        self,
        insights,
        code_result,
        post_code_insights,
        log_read,
        kb_read,
        manual_kb_read,
        rater_feedback,
        suggestion,
    ):
        class KBUpdate(BaseModel):
            knowledge_base_content: str
            suggestion: str
            summary: str
            rating: int

        knowledge_agent = Agent(
            "Knowledge_Agent",
            """An LLM has just written some code. You will be given the code and the output from the runs. You will also be given a knowledge database. Your job is to curate that knowledge database to help the coder. The coder will be able to reference your knowledge db. Help it to improve. Be creative. Try to expand the knowledge base and not just rewrite. Try not to lose lessons learned and keep growing it. You can let me know if there is any tool that will help you through suggestions. Summarize the actions the coder took. Suggest 1 next step for the coder to take.
            Determine whether the code has completed the stated goal and whether or not we can move on to the next task. The code should be feature complete and well tested. Your rating should be one of the following: 1. Reject 2. Accept with changes 3. Accept as is
            """,
        )

        # There is a Code Reviewer who rates the code. You'll be given feedback from them as well.
        # ## pre run insights
        # {insights}

        # ## Actions log
        # {log_read}

        # ## Your knowledge db
        # {kb_read}

        # ## Rater Feedback
        # {rater_feedback}

        return knowledge_agent(
            f"""
        ## User Story goal
        {self.goal}

        ## Last AI provided next step suggestion
        {suggestion}

        ## Coder action
        {code_result}

        ## Post run insights
        {post_code_insights}
        """,
            KBUpdate,
        )

    def rater(self, code_result, post_code_insights):
        class Rating(BaseModel):
            rating: int
            reason: str

        rater = Agent(
            "Rater",
            "Act as a code reviewer. You'll be given code written by a coding AI. It's your job to determine whether the code has completed the stated goal and whether or not we can move on to the next task. The code should be feature complete and well tested. Provide your reasoning for the rating you give. Your rating should be one of the following: 1. Reject 2. Accept with changes 3. Accept as is",
        )

        return rater(
            f"""
        ## Code Result
        {code_result}

        ## Post run insights
        {post_code_insights}
        """,
            Rating,
        )

    async def flow_w_termination(self):
        insights = await self.get_insights()
        print(insights)

        context = self.get_context(insights)
        logs = self.read_logs()
        kb_read = logs["kb_read"]
        log_read = logs["log_read"]
        manual_kb_read = logs["manual_kb_read"]

        code_result = self.code_action(
            insights=insights, context=context, log_read=log_read, kb_read=kb_read
        )

        logger.info(
            json.dumps(
                {
                    "code_result": code_result.code,
                    "code_filename": code_result.filename,
                    "code_reason": code_result.reason,
                },
                indent=2,
            )
        )

        self.utils.write_string_to_file(code_result.filename, code_result.code)

        post_code_insights = await self.get_insights()

        logger.info(post_code_insights)

        rater = self.rater(
            code_result=json.dumps(code_result.dict()),
            post_code_insights=post_code_insights,
        )

        kb_admin_result = self.knowledge_base_admin(
            insights=insights,
            code_result=code_result,
            post_code_insights=post_code_insights,
            log_read=log_read,
            kb_read=kb_read,
            manual_kb_read=manual_kb_read,
            rater_feedback=rater.reason,
        )

        logger.info(
            json.dumps(
                {
                    "kb_summary": kb_admin_result.summary,
                    "kb_suggestion": kb_admin_result.suggestion,
                    "rating": rater.rating,
                    "reason": rater.reason,
                    "filename": code_result.filename,
                    "kb_rating": kb_admin_result.rating,
                },
                indent=2,
            )
        )

        use_file_logger()

        logger.info(
            json.dumps(
                {
                    "goal": self.goal,
                    "kb_summary": kb_admin_result.summary,
                    "suggestion": kb_admin_result.suggestion,
                    "post_code_insight": post_code_insights,
                    "prev_code_insights": insights,
                    "code": code_result.code,
                    "filename": code_result.filename,
                    "reason": code_result.reason,
                    "rating": rater.rating,
                }
            )
        )

        self.write_logs(
            kb_content=kb_admin_result.knowledge_base_content,
            summary=kb_admin_result.summary,
            suggestion=kb_admin_result.suggestion,
        )

    async def flow_w_meta_goal(self):
        last_suggestion = self.get_last_suggestion()
        insights = await self.get_insights()
        print(insights)

        context = self.get_context(insights)
        logs = self.read_logs()
        kb_read = logs["kb_read"]
        log_read = logs["log_read"]
        manual_kb_read = logs["manual_kb_read"]

        code_result = self.code_action(
            insights=insights,
            context=context,
            log_read=log_read,
            kb_read=kb_read,
            suggestion=last_suggestion,
        )

        logger.info(
            json.dumps(
                {
                    "code_result": code_result.code,
                    "code_filename": code_result.filename,
                    "code_reason": code_result.reason,
                },
                indent=2,
            )
        )

        self.utils.write_string_to_file(code_result.filename, code_result.code)

        post_code_insights = await self.get_insights()

        logger.info(post_code_insights)

        rater = self.rater(
            code_result=json.dumps(code_result.dict()),
            post_code_insights=post_code_insights,
        )

        kb_admin_result = self.knowledge_base_admin(
            insights=insights,
            code_result=code_result,
            post_code_insights=post_code_insights,
            log_read=log_read,
            kb_read=kb_read,
            manual_kb_read=manual_kb_read,
            rater_feedback=rater.reason,
            suggestion=last_suggestion,
        )

        logger.info(
            json.dumps(
                {
                    "kb_summary": kb_admin_result.summary,
                    "kb_suggestion": kb_admin_result.suggestion,
                    "rating": rater.rating,
                    "reason": rater.reason,
                    "filename": code_result.filename,
                    "kb_rating": kb_admin_result.rating,
                },
                indent=2,
            )
        )

        use_file_logger()

        logger.info(
            json.dumps(
                {
                    "goal": self.goal,
                    "kb_summary": kb_admin_result.summary,
                    "suggestion": kb_admin_result.suggestion,
                    "post_code_insight": post_code_insights,
                    "prev_code_insights": insights,
                    "code": code_result.code,
                    "filename": code_result.filename,
                    "reason": code_result.reason,
                    "rating": rater.rating,
                }
            )
        )

        self.write_logs(
            kb_content=kb_admin_result.knowledge_base_content,
            summary=kb_admin_result.summary,
            suggestion=kb_admin_result.suggestion,
        )


if __name__ == "__main__":
    root_dir = "py_demo"
    goal = """Handle more metrics passed in swing data"""
    language = "Python"

    simple_flow = Flow(root_dir=root_dir, goal=goal, language=language)
    asyncio.run(Flow.flow_w_termination())
