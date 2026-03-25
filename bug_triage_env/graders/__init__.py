"""Grader registry mapping task IDs to scoring functions."""

from . import task1_grader, task2_grader, task3_grader

GRADERS = {
    "task_1": task1_grader.grade,
    "task_2": task2_grader.grade,
    "task_3": task3_grader.grade,
}

__all__ = ["GRADERS", "task1_grader", "task2_grader", "task3_grader"]
