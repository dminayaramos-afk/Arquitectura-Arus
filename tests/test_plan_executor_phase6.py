from agents.tool_agent import ToolAgent
from planning.planner import Planner
from planning.plan_executor import PlanExecutor


def test_plan_execution():

    planner = Planner()
    agent = ToolAgent()

    plan = planner.plan(
        "suma 2 3"
    )

    executor = PlanExecutor(agent)

    results = executor.execute(
        plan
    )

    assert len(results) == 1
    assert results[0].success
    assert results[0].answer == "5"
