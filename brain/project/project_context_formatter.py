from .project_context import ProjectContext


class ProjectContextFormatter:

    @staticmethod
    def format(context: ProjectContext) -> str:
        lines = [
            "PROJECT CONTEXT",
            f"Project: {context.project_name}",
            f"Status: {context.project_status}",
        ]

        # ---------------------------------------------------------
        # PROJECT PROGRESS
        # ---------------------------------------------------------

        completed_tasks = sum(
            1
            for task in context.tasks
            if task["status"] == "completed"
        )

        active_tasks = sum(
            1
            for task in context.tasks
            if task["status"] == "active"
        )

        pending_tasks = sum(
            1
            for task in context.tasks
            if task["status"] == "pending"
        )

        total_tasks = len(context.tasks)

        completion_percentage = (
            round((completed_tasks / total_tasks) * 100)
            if total_tasks
            else 0
        )

        lines.append(
            f"Task Progress: {completion_percentage}% "
            f"({completed_tasks}/{total_tasks} completed)"
        )

        lines.append(
            f"Task Status: {active_tasks} active, "
            f"{pending_tasks} pending"
        )

        if context.project_description:
            lines.append(
                f"Description: {context.project_description}"
            )

        # ---------------------------------------------------------
        # GOALS
        # ---------------------------------------------------------

        lines.append("")
        lines.append("GOALS:")

        if context.goals:
            for goal in context.goals:
                lines.append(
                    f"- {goal['title']} "
                )
                lines.append(
                    f"(status: {goal['status']})"
        )

                if goal.get("description"):
                    lines.append(
                        f"  Description: {goal['description']}"
            )

                goal_tasks = [
                    task
                    for task in context.tasks
                    if task.get("goal_id") == goal["goal_id"]
        ]

                goal_total_tasks = len(goal_tasks)

                goal_completed_tasks = sum(
                     1
                    for task in goal_tasks
                    if task["status"] == "completed"
        )

                goal_completion_percentage = (
                    round(
                        (goal_completed_tasks / goal_total_tasks) * 100
            )
                    if goal_total_tasks
                    else 0
        )

                lines.append(
                    f"  Goal Progress: "
                    f"{goal_completion_percentage}% "
                    f"({goal_completed_tasks}/"
                    f"{goal_total_tasks} completed)"
                )
                goal_status = goal["status"]

                if goal_status == "completed" and goal_total_tasks > goal_completed_tasks:
                    lines.append(
                "  CONSISTENCY WARNING: "
                "Goal is marked completed, but "
                "not all assigned tasks are completed."
            )

                if (
            goal_status != "completed"
            and goal_total_tasks > 0
            and goal_completed_tasks == goal_total_tasks
        ):
                    lines.append(
                "  CONSISTENCY NOTE: "
                "All assigned tasks are completed, "
                "but the goal is not marked completed."
            )
        else:
            lines.append("- No goals")

        # ---------------------------------------------------------
        # TASKS
        # ---------------------------------------------------------

        lines.append("")
        lines.append("TASKS:")

        if context.tasks:
            grouped_tasks: dict[str | None, list[dict]] = {}
            unassigned_tasks: list[dict] = []

            known_goal_ids = {
                goal["goal_id"]
                for goal in context.goals
            }

            for task in context.tasks:
                goal_id = task.get("goal_id")

                if goal_id and goal_id in known_goal_ids:
                    grouped_tasks.setdefault(
                        goal_id,
                        []
                    ).append(task)
                else:
                    unassigned_tasks.append(task)

            goal_titles = {
                goal["goal_id"]: goal["title"]
                for goal in context.goals
            }

            # -----------------------------------------------------
            # TASKS GROUPED BY GOAL
            # -----------------------------------------------------

            for goal_id, goal_tasks in grouped_tasks.items():
                goal_title = goal_titles.get(
                    goal_id,
                    "Unknown goal",
                )

                lines.append(
                    f"GOAL: {goal_title}"
                )

                for task in goal_tasks:
                    lines.append(
                        f"- {task['title']} "
                        f"(status: {task['status']})"
                    )

                    if task.get("description"):
                        lines.append(
                            f"  Description: {task['description']}"
                        )

                lines.append("")

            # -----------------------------------------------------
            # UNASSIGNED TASKS
            # -----------------------------------------------------

            if unassigned_tasks:
                lines.append("UNASSIGNED TASKS:")

                for task in unassigned_tasks:
                    lines.append(
                        f"- {task['title']} "
                        f"(status: {task['status']})"
                    )

                    if task.get("description"):
                        lines.append(
                            f"  Description: {task['description']}"
                        )

                lines.append("")

        else:
            lines.append("- No tasks")



                    # ---------------------------------------------------------
        # WORK STATE SUMMARY
        # ---------------------------------------------------------

        if context.tasks:
            paused_tasks = [
                task
                for task in context.tasks
                if task["status"] == "paused"
            ]

            pending_tasks = [
                task
                for task in context.tasks
                if task["status"] == "pending"
            ]

            active_tasks = [
                task
                for task in context.tasks
                if task["status"] == "active"
            ]

            if paused_tasks:
                lines.append("")
                lines.append("PAUSED WORK:")

                for task in paused_tasks:
                    lines.append(
                        f"- {task['title']}"
                    )

                    if task.get("description"):
                        lines.append(
                            f"  Description: {task['description']}"
                        )

            if pending_tasks:
                lines.append("")
                lines.append("PENDING WORK:")

                for task in pending_tasks:
                    lines.append(
                        f"- {task['title']}"
                    )

            if active_tasks:
                lines.append("")
                lines.append("ACTIVE WORK:")

                for task in active_tasks:
                    lines.append(
                        f"- {task['title']}"
                    )

                            # ---------------------------------------------------------
        # NEXT WORK CANDIDATES
        # ---------------------------------------------------------

        if context.tasks:
            next_work_candidates = [
                task
                for task in context.tasks
                if task["status"] == "active"
            ]

            if not next_work_candidates:
                next_work_candidates = [
                    task
                    for task in context.tasks
                    if task["status"] == "pending"
                ]

            if next_work_candidates:
                lines.append("")
                lines.append("NEXT WORK CANDIDATES:")

                for task in next_work_candidates:
                    lines.append(
                        f"- {task['title']} "
                        f"(status: {task['status']})"
                    )

                    if task.get("description"):
                        lines.append(
                            f"  Description: {task['description']}"
                        )

                                # DECISIONS
        lines.append("")
        lines.append("DECISIONS:")

        if context.decisions:
            for decision in context.decisions:
                lines.append(
                    f"- {decision['title']} "
                    f"(status: {decision['status']})"
                )

                if decision.get("description"):
                    lines.append(
                        f"  Description: "
                        f"{decision['description']}"
                    )

                if decision.get("reason"):
                    lines.append(
                        f"  Reason: "
                        f"{decision['reason']}"
                    )
        else:
            lines.append("- No decisions")

        return "\n".join(lines)