from executor.docker_runner import (
    docker_executor,
    extract_coverage_warnings,
    convert_overall_debt_to_minutes,
)

import pytest
import asyncio


@pytest.fixture
def example_stdout():
    return """
------------------------------ Captured stdout call -------------------------------

Welcome to Gradle 8.0.2!

Here are the highlights of this release:
 - Improvements to the Kotlin DSL
 - Fine-grained parallelism from the first build with configuration cache
 - Configurable Gradle user home cache cleanup

For more details see https://docs.gradle.org/8.0.2/release-notes.html

Starting a Gradle Daemon (subsequent builds will be faster)
> Task :clean
> Task :processResources
> Task :processTestResources NO-SOURCE

> Task :detekt
naming - 10min debt
        FunctionNaming - [not_home] at /workspaces/swing-transformer-demo/transformer/src/main/kotlin/app/Application.kt:24:9
        MemberNameEqualsClassName - [simpleTest] at /workspaces/swing-transformer-demo/transformer/src/test/kotlin/SimpleTest.kt:6:5
performance - 20min debt
        SpreadOperator - [main] at /workspaces/swing-transformer-demo/transformer/src/main/kotlin/app/Application.kt:12:32
style - 30min debt
        FunctionOnlyReturningConstant - [home] at /workspaces/swing-transformer-demo/transformer/src/main/kotlin/app/Application.kt:19:9
        FunctionOnlyReturningConstant - [not_home] at /workspaces/swing-transformer-demo/transformer/src/main/kotlin/app/Application.kt:24:9
        NewLineAtEndOfFile - [ErrorController.kt] at /workspaces/swing-transformer-demo/transformer/src/main/kotlin/app/ErrorController.kt:1:1
        NewLineAtEndOfFile - [SimpleTest.kt] at /workspaces/swing-transformer-demo/transformer/src/test/kotlin/SimpleTest.kt:1:1

Overall debt: 1h


> Task :compileKotlin
> Task :compileJava NO-SOURCE
> Task :classes
> Task :jar
> Task :inspectClassesForKotlinIC
> Task :resolveMainClassName
> Task :bootJar
> Task :assemble
> Task :compileTestKotlin
> Task :compileTestJava NO-SOURCE
> Task :testClasses UP-TO-DATE
> Task :test
> Task :jacocoTestReport

> Task :checkCoverage
WARNING: Instruction coverage is below 80%: 0.0%
WARNING: Branch coverage is below 80%: 0.0%

> Task :check
> Task :build

BUILD SUCCESSFUL in 42s
12 actionable tasks: 12 executed
    """


@pytest.mark.skip("Takes too long")
@pytest.mark.asyncio
async def test_docker_executor_runs():
    result = await docker_executor()

    assert hasattr(result, "stdout")
    assert hasattr(result, "overall_debt")
    assert hasattr(result, "coverage_warnings")


def test_extract_coverage_warnings(example_stdout):
    coverage_warnings = extract_coverage_warnings(example_stdout)
    assert coverage_warnings == {"Instruction": 0.0, "Branch": 0.0}


def test_overall_debt(example_stdout):
    overall_debt = convert_overall_debt_to_minutes(example_stdout)
    assert overall_debt == 60
