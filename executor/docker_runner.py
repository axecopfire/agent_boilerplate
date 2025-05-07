import json
import docker
import uuid
import asyncio
import os
import re
from docker.errors import ImageNotFound
from library.utils.logging_config import logger


def extract_coverage_warnings(text):
    # Define the regex pattern to match the checkCoverage warnings
    pattern = r"WARNING: (Instruction|Branch) coverage is below 80%: (\d+\.\d+)%"
    matches = re.findall(pattern, text)

    coverage = {}

    for match in matches:
        coverage_type = match[0]
        percentage = float(match[1])
        coverage[coverage_type] = percentage

    return coverage


def convert_overall_debt_to_minutes(text):
    # Define the regex pattern to match the "Overall debt" line
    pattern = r"Overall debt: ((\d+)\s*(h|min|day|days)\s*)+"
    match = re.search(pattern, text)

    if not match:
        return None

    overall_debt_string = match.group(0)

    # Define the regex pattern to match the time value and unit
    time_pattern = r"(\d+)\s*(h|min|day|days)"
    matches = re.findall(time_pattern, overall_debt_string)

    total_minutes = 0

    for value, unit in matches:
        value = int(value)

        if unit in ["minute", "min"]:
            total_minutes += value
        elif unit in ["h"]:
            total_minutes += value * 60
        elif unit in ["day", "days"]:
            total_minutes += value * 60 * 8
        else:
            raise ValueError(f"Unknown time unit: {unit}")

    return total_minutes


async def _wait_for_ready(container, timeout: int = 60, stop_time: float = 0.1) -> None:
    elapsed_time = 0.0

    while container.status != "running" and elapsed_time < timeout:
        await asyncio.sleep(stop_time)
        elapsed_time += stop_time

        await asyncio.to_thread(container.reload)
        continue

    if container.status != "running":
        raise ValueError("Container failed to start")

    return "Container is ready!"


async def docker_executor():
    host_pwd = os.getenv("HOST_PWD")  # Got this from the devcontainer
    client = docker.from_env()

    image = "gradle:8.0-jdk17"

    logger.info("Generating Code Insights")

    # Pull the image if it is not available locally
    try:
        await asyncio.to_thread(client.images.get, image)
    except ImageNotFound:
        await asyncio.to_thread(client.images.pull, image)

    container = client.containers.create(
        image,
        name=f"tmp-{uuid.uuid4()}",
        entrypoint="/bin/sh",
        tty=True,
        detach=True,
        auto_remove=True,
        volumes={os.getenv("HOST_PWD"): {"bind": "/workspaces", "mode": "rw"}},
        working_dir="/workspaces",
    )

    await asyncio.to_thread(container.start)

    await _wait_for_ready(container)

    # Do everything in here. Keep it running? Do I want to do sandbox?
    res = await asyncio.to_thread(
        container.exec_run, "./swing-transformer-demo/executor/run_gradle.sh"
    )

    try:
        await asyncio.to_thread(container.stop)
        await asyncio.to_thread(container.wait)
    except Exception as e:
        print(f"Error cleaning up container: {e}")

    stdout = res.output.decode()
    overall_debt = convert_overall_debt_to_minutes(stdout)
    coverage_warnings = extract_coverage_warnings(stdout)

    return {
        "stdout": stdout,
        "overall_debt": overall_debt,
        "coverage_warnings": coverage_warnings,
    }
