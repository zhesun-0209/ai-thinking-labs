"""Run MCTS regressions from the notebook source without downloads or plotting."""

import ast
import math
from collections import defaultdict

import numpy as np
import pandas as pd

from notebook_content.ch08 import MCTS_CELL, MCTS_INTRO_CELL, MCTS_VALIDATE_CELL


def load_mcts():
    namespace = {"np": np, "pd": pd, "math": math, "defaultdict": defaultdict}
    # Load environment data/functions, stopping before figure creation.
    intro_nodes = []
    for node in ast.parse(MCTS_INTRO_CELL).body:
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "subplots"):
            break
        intro_nodes.append(node)
    exec(compile(ast.Module(body=intro_nodes, type_ignores=[]), "MCTS_INTRO_CELL", "exec"), namespace)
    algorithm_nodes = []
    for node in ast.parse(MCTS_CELL).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "root_plan" for target in node.targets
        ):
            break
        algorithm_nodes.append(node)
    exec(compile(ast.Module(body=algorithm_nodes, type_ignores=[]), "MCTS_CELL", "exec"), namespace)
    comparison_functions = [node for node in ast.parse(MCTS_VALIDATE_CELL).body if isinstance(node, ast.FunctionDef)]
    exec(compile(ast.Module(body=comparison_functions, type_ignores=[]), "MCTS_VALIDATE_CELL", "exec"), namespace)
    return namespace


def main():
    env = load_mcts()
    backpropagate, mcts_plan = env["backpropagate"], env["mcts_plan"]
    root_state, goal_state = env["root_state"], env["goal_state"]
    horizon, budget = env["MCTS_HORIZON"], env["MCTS_BUDGET"]
    test_n, test_na, test_w = defaultdict(int), defaultdict(int), defaultdict(float)
    test_path = [((0, 3), 0, 1.0), ((0, 2), 0, 2.0), ((1, 1), 1, 3.0)]
    test_return = backpropagate(test_path, 0.0, 0.5, test_n, test_na, test_w)
    assert np.isclose(test_return, 2.75)
    assert np.allclose([test_w[key, action] for key, action, _ in test_path], [2.75, 3.5, 3.0])
    assert (0, 3) != (0, 2) and len(test_n) == 3
    assert np.isclose(backpropagate([((0, 2), 0, 1.0)], 2.0, 0.5,
                                   defaultdict(int), defaultdict(int), defaultdict(float)), 2.0)
    assert mcts_plan(goal_state, 10)["action"] is None
    assert mcts_plan(5, 10)["action"] is None
    assert mcts_plan(root_state, 0)["action"] is None
    assert all(np.isclose(sum(item[0] for item in outcomes), 1.0) for outcomes in env["model_outcomes"].values())
    for remaining in [1, 2, 18]:
        probe = mcts_plan(root_state, remaining, simulations=40, seed=31, trace_count=40)
        assert all(row["总步数"] <= remaining and row["扩展新动作数"] <= 1 for row in probe["traces"])
        assert probe["table"]["visits"].sum() == 40
        assert all(0 < key[1] <= remaining for key in probe["N_state"])
        assert probe["table"].loc[0, "visits"] == probe["table"]["visits"].max()
    pd.testing.assert_frame_equal(
        mcts_plan(root_state, horizon, budget, seed=12)["table"],
        mcts_plan(root_state, horizon, budget, seed=12)["table"],
    )
    random_evaluation = env["evaluate_policy"](False)
    mcts_evaluation = env["evaluate_policy"](True)
    assert mcts_evaluation["成功"].mean() > random_evaluation["成功"].mean() + 0.25
    assert mcts_evaluation["折扣回报"].mean() > random_evaluation["折扣回报"].mean() + 0.3
    assert mcts_evaluation["成功"].mean() >= 0.4
    assert np.isfinite(mcts_evaluation["折扣回报"]).all()
    assert mcts_evaluation["步数"].between(1, horizon).all()
    print("PASS: MCTS backup, horizon, visits, terminal states, reproducibility and policy comparison")


if __name__ == "__main__":
    main()
