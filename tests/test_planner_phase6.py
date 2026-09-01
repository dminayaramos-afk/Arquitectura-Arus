from planning.planner import Planner


def test_plan_suma():

    planner = Planner()

    plan = planner.plan(
        "suma 2 3"
    )

    assert plan.goal == "suma 2 3"
    assert len(plan.steps) == 1
    assert plan.steps[0].action == "suma"


def test_plan_resta():

    planner = Planner()

    plan = planner.plan(
        "resta 10 3"
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].action == "resta"


def test_plan_multiplica():

    planner = Planner()

    plan = planner.plan(
        "multiplica 4 5"
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].action == "multiplica"


def test_plan_divide():

    planner = Planner()

    plan = planner.plan(
        "divide 10 2"
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].action == "divide"


def test_plan_desconocido():

    planner = Planner()

    plan = planner.plan(
        "hola arus"
    )

    assert plan.is_empty()
