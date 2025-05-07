import json
from utils import Utils
from library.agents.base_agent import Agent
from typing import List
from pydantic import BaseModel
from library.utils.logging_config import logger

"""
Get State of Repo
Generate Acceptance Criteria
Generate Test Specs
"""


class GenerateCodingStrategy:

    def __init__(self, goal, root_dir="./", language="Python"):
        self.utils = Utils(root_dir, language)
        self.root_dir = root_dir
        self.goal = goal
        self.language = language

    def generate_files_needed_to_read(self, goal, folder_structure):

        class FilesNeeded(BaseModel):
            files: List[str]

        logger.info("Generating files needed to read")
        files = Agent(
            "files_needed",
            f"""You are given a coding goal and a folder structure. Based on this context, your task is to generate a list of all the files that could possibly be useful to read to accomplish the goal. Only return filenames that actually exist in the project's folder_structure. Be as thorough as possible and consider the following key areas:

1. **Core Implementation Files:**
   - Identify files that are directly related to the core functionality required to achieve the goal.
   - Include files that define key classes, functions, and modules.

2. **Configuration Files:**
   - Identify configuration files that might need to be reviewed or modified.
   - There are hidden files in the directory list that you should not try to retrieve such as .env.

3. **Dependency Files:**
   - Identify files that manage dependencies and packages.
   - Include files such as `requirements.txt`, `Pipfile`, `package.json`, `build.gradle`, etc.

4. **Test Files:**
   - Identify test files that are relevant to the goal.
   - Include unit tests, integration tests, and any other relevant test files.

5. **Documentation Files:**
   - Identify documentation files that provide context or instructions related to the goal.
   - Include README.md, `CONTRIBUTING.md`, and any other relevant documentation.

6. **Scripts and Utilities:**
   - Identify scripts and utility files that might be useful.
   - Include any helper scripts, build scripts, or automation scripts.
        """,
        )

        prompt = f"""
## Goal
{goal}

## Folder Structure
{folder_structure}
        """
        read_list = files(prompt, FilesNeeded)

        logger.info(json.dumps(read_list.files))
        return read_list

    def build_acceptance_criteria(self, goal, folder_structure, code_insights):
        acceptance_criteria = Agent(
            "acceptance_criteria",
            f"""You are given a coding goal, a folder structure, and the results of unit tests and linting. Based on this context, your task is to generate acceptance criteria tests for the goal. The acceptance criteria should be specific, measurable, achievable, relevant, and time-bound (SMART). Consider the following key areas:

1. **Functionality:**
   - Define the specific features or functionalities that need to be implemented or improved.
   - Ensure the criteria are clear and unambiguous.

2. **Performance:**
   - Specify any performance benchmarks or requirements.
   - Include criteria for response times, throughput, and resource utilization.

3. **Security:**
   - Identify any security requirements or standards that must be met.
   - Include criteria for data protection, authentication, and authorization.

4. **Usability:**
   - Define any usability requirements.
   - Include criteria for user interface design, accessibility, and user experience.

5. **Compatibility:**
   - Specify any compatibility requirements.
   - Include criteria for supported browsers, devices, and operating systems.

6. **Testing:**
   - Define the testing requirements.
   - Include criteria for unit tests, integration tests, and end-to-end tests.

7. **Documentation:**
   - Specify any documentation requirements.
   - Include criteria for code comments, user manuals, and API documentation.        
        """,
        )

    def build_coding_strategy(self, folder_structure, code_insights, files_of_interest):

        class Strategy(BaseModel):
            coding_strategy: str
            reason: str

        class Strategies(BaseModel):
            coding_strategies: List[Strategy]

            logger.info("Building coding strategy")

        strategy = Agent(
            "coding_strategy",
            f"""The user will give you:
- Files of interest for the project 
- The folder structure of the project
- The results of unit tests and linting
- Their goal for a feature or a system
        
Based on this context, your task is to decompose the overall goal into smaller, manageable tasks for LLMs to accomplish. Build focused coding strategies tailored to accomplish the user's goal. Functionality needs to be your top priority. If the code is broken and the build is failing. You need to work on fixing it before it can be improved. The strategies should address the following key areas:

- Functionality: What features need to be implemented or improved? What bugs need to be fixed?
- Code Quality: What code smells need to be refactored?
- Testing: What tests need to be written or improved?
- Documentation: What documentation needs to be updated or created? 

Structured output should be a list of coding goals to accomplish. Each goal should be accompanied by a brief rationale explaining why it is necessary to achieve the overall goal. The goals should be specific, actionable, and achievable within a reasonable timeframe.
        """,
        )

        prompt = f"""
        ## Files marked as of interest
        {files_of_interest}

        ## Goal
        {self.goal}

        ## Folder Structure
        {folder_structure}

        ## Code Insights
        {code_insights}
        """

        return strategy(prompt, Strategies)

    def get_context(self):
        folder_structure = self.utils.get_folder_structure()

        file_list = self.generate_files_needed_to_read(self.goal, folder_structure)

        file_contents_str = ""

        for file in file_list.files:
            file_contents = self.utils.read_file_to_string(file)
            if file_contents:
                file_contents_str += f"## {file}\n{file_contents}\n"

        return {
            "file_contents_str": file_contents_str,
            "folder_structure": folder_structure,
        }

    def code_action(self, code_insights):
        """
        - Utils Get Code Insights
            - Run Docker Executer to get Gradle Build
        - Get file reader context (is there a better way to return a more thorough file reader context?)
            - pass in code insights and goal
            - Should return found functions
            - all file names (get_folder_structure)
        - Should critic on whether all helpful files and functions were found
        """

        logger.info("Generating code action")

        context = self.get_context()
        strategies = self.build_coding_strategy(
            folder_structure=context["folder_structure"],
            code_insights=code_insights,
            files_of_interest=context["file_contents_str"],
        )

        coding_actions = dict()

        coded_strategies = []

        for strategy in strategies.coding_strategies:
            code = self.write_code(
                strategy.coding_strategy, context["file_contents_str"]
            )

            # Sort Code proposals by file
            for proposal in code.proposals:
                if coding_actions.get(proposal.filename):
                    coding_actions[proposal.filename].append(proposal)
                else:
                    coding_actions[proposal.filename] = [proposal]

        aggregated_code = self.aggregate_code_writing(coding_actions)

        for code in aggregated_code:
            self.utils.write_string_to_file(code["filename"], f"{code['code']}\n")

        return aggregated_code

    def aggregate_code_writing(self, code_writing_proposals):

        flattened_proposals = []
        aggregated_proposals = []
        logger.info("Aggregating code writing proposals")

        class CodeWritingAggregate(BaseModel):
            code: str
            reason: str

        # Convert code_writing_proposals object into a list of proposals to aggregate
        for filename, proposals in code_writing_proposals.items():

            # No need to aggregate if there is only one proposal
            if len(proposals) < 2:
                aggregated_proposals.append(
                    {
                        "code": proposals[0].code,
                        "reason": proposals[0].reason,
                        "filename": filename,
                    }
                )
                continue

            proposal_text = ""

            for proposal in proposals:
                proposal_text += f"## Proposal for {filename}\n{proposal.code}\nReason: {proposal.reason}\n"

            flattened_proposals.append(
                {"proposal_text": proposal_text, "filename": filename}
            )

        for proposal in flattened_proposals:

            aggregate_proposal = Agent(
                "code_writing_aggregate",
                f"""
                You are given a list of code writing proposals. Based on this context, your task is to aggregate the proposals into a single code file. The document should merge all the code writing proposals along with the reasoning provided by each developer. Just provide the contents of the code file
            """,
            )

            code_writing_aggregate = aggregate_proposal(
                proposal["proposal_text"], CodeWritingAggregate
            )

            aggregated_proposals.append(
                {
                    "code": code_writing_aggregate.code,
                    "filename": proposal["filename"],
                    "reason": code_writing_aggregate.reason,
                }
            )

        return aggregated_proposals

    def write_code(self, goal, context):
        class CodeWriterProposal(BaseModel):
            code: str
            filename: str
            reason: str

        class CodeWriterProposals(BaseModel):
            proposals: List[CodeWriterProposal]

        code_writer = Agent(
            "code_writer",
            f"""
        Act as a senior software developer. You'll be given a coding goal and context of the project. Based on this context, your task is to write code that accomplishes the goal. Make sure the code is relevant to the application and provide your reasoning for the code. The code should be clean, well-structured, and thoroughly tested. Your top priority is to maintain functionality and to introduce as few bugs and breaking changes as possible. Take your time. The quality and functionality of your code is more important than the quantity.
        """,
        )

        prompt = f"""
        ## Goal
        {goal}

        ## Context
        {context}
        """

        logger.info("Writing code")

        return code_writer(prompt, CodeWriterProposals)
