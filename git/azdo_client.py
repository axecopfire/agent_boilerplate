# from msrest.authentication import BasicAuthentication, BasicTokenAuthentication
from azure.devops.connection import Connection
from azure.devops.credentials import BasicAuthentication
import os
import json


import logging

logger = logging.getLogger(__name__)


class AzdoClient:
    def __init__(self):
        personal_access_token = os.getenv("AZDO_PAT")
        organization_url = os.getenv("AZDO_ORG_URL")
        # Create a connection to the Azure DevOps organization
        credentials = BasicAuthentication("", personal_access_token)
        connection = Connection(base_url=organization_url, creds=credentials)

        self.connection = connection

    def init_ai_pr(self, main_ai_branch_name, goal):

        # Get a client (the "core" client provides access to projects, teams, etc)
        core_client = self.connection.clients.get_core_client()
        git_client = self.connection.clients.get_git_client()

        # Get the list of projects in the organization
        projects = core_client.get_projects()
        project = None
        for p in projects:
            print(p.name)
            if p.name == "Hermes Crew":
                project = p
                break

        # Get all repos and filter the only one we want to work with
        repos = git_client.get_repositories(project.id)
        repo = None
        for r in repos:
            if r.name == "agentic-research-demos":
                repo = r
                break

        branches = git_client.get_branches(repo.id, project.id)
        main_ai_branch = None

        for b in branches:
            if main_ai_branch_name == b.name:
                main_ai_branch = b
                break

        try:
            pr = git_client.create_pull_request(
                git_pull_request_to_create={
                    "source_ref_name": f"refs/heads/{main_ai_branch.name}",
                    "target_ref_name": "refs/heads/main",
                    "title": f"AI PR for branch {main_ai_branch.name}",
                    "description": f"Stated Goal: {goal}",
                },
                repository_id=repo.id,
                project=project.id,
            )
            return pr
        except Exception as e:
            if (
                "An active pull request for the source and target branch already exists."
                in str(e)
            ):
                return "PR already exists"
