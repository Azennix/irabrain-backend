from typing import Any


class VisualIntelligenceService:
    """
    Coordinates visual generation for IRABRAIN.

    The LLM decides whether a visual is useful and chooses its
    representation. This service enforces the single-visual contract.
    """

    def __init__(self, chat_engine):
        self.chat_engine = chat_engine

    def should_generate(self, query: str) -> bool:
        """
        Delegate the semantic decision to the LLM.
        Do not hardcode message keywords or greeting rules here.
        """
        return bool(query and query.strip())

    def generate(
        self,
        query: str,
        response: str,
        context,
    ) -> dict[str, Any] | None:
        visuals = self.generate_multi(query, response, context)
        return visuals[0] if visuals else None

    def generate_multi(
        self,
        query: str,
        response: str,
        context,
    ) -> list[dict[str, Any]]:
        """
        Return zero or one visual object.

        A single visual may contain multiple connected nodes and edges.
        Different visual types may use different payload structures.
        """

        if not self.should_generate(query):
            return []

        try:
            generator = getattr(
                self.chat_engine,
                "generate_visuals",
                None,
            )

            if not callable(generator):
                print(
                    "[VISUAL] No generate_visuals method is available; "
                    "skipping visual generation."
                )
                return []

            result = generator(
                user_message=query,
                assistant_response=response,
                request_context=context,
            )

            if result is None:
                return []

            # Support a single object or a legacy one-item list.
            if isinstance(result, dict):
                visual = result

            elif isinstance(result, list):
                if len(result) != 1:
                    print(
                        "[VISUAL WARNING] Expected zero or one visual; "
                        f"received {len(result)}. Discarding result."
                    )
                    return []

                visual = result[0]

            else:
                print("[VISUAL WARNING] Invalid visual result type.")
                return []

            if not isinstance(visual, dict):
                return []

            visual_type = visual.get("type")

            if visual_type in (None, "none"):
                return []

            # Every visual must have a valid title.
            title = visual.get("title")

            if not isinstance(title, str) or not title.strip():
                print("[VISUAL WARNING] Visual has no valid title.")
                return []

            # --------------------------------------------------
            # BUSINESS MODEL CANVAS VALIDATION
            # --------------------------------------------------

            if visual_type == "business_model_canvas":

                canvas = visual.get("canvas")

                required_sections = {
                    "key_partners",
                    "key_activities",
                    "key_resources",
                    "value_propositions",
                    "customer_relationships",
                    "channels",
                    "customer_segments",
                    "cost_structure",
                    "revenue_streams",
                }

                if not isinstance(canvas, dict):
                    print(
                        "[VISUAL WARNING] Business Model Canvas "
                        "has an invalid canvas structure."
                    )
                    return []

                if not required_sections.issubset(canvas.keys()):
                    print(
                        "[VISUAL WARNING] Business Model Canvas "
                        "is missing required sections."
                    )
                    return []

                # Every section must contain a list of strings.
                for section in required_sections:
                    items = canvas.get(section)

                    if not isinstance(items, list):
                        print(
                            f"[VISUAL WARNING] Invalid canvas section: "
                            f"{section}"
                        )
                        return []

                    if any(not isinstance(item, str) for item in items):
                        print(
                            f"[VISUAL WARNING] Invalid item in canvas "
                            f"section: {section}"
                        )
                        return []

                # Limit content to keep the canvas readable.
                visual["canvas"] = {
                    section: [
                        item.strip()[:300]
                        for item in canvas[section][:8]
                        if item.strip()
                    ]
                    for section in required_sections
                }

                visual["title"] = title.strip()[:200]

                print(
                    "[VISUAL] Validated Business Model Canvas."
                )

                return [visual]

                        # --------------------------------------------------
            # TYPE-SPECIFIC VISUAL VALIDATION
            # --------------------------------------------------

            allowed_types = {
                "flowchart",
                "concept_map",
                "steps",
                "comparison",
                "system_architecture",
                "connection_graph",
                "hierarchy",
                "decision_tree",
                "cycle",
                "timeline",
                "data_chart",
                "mind_map",
                "blueprint",
            }

            if visual_type not in allowed_types:
                print(f"[VISUAL WARNING] Unsupported visual type: {visual_type}")
                return []

            visual["title"] = title.strip()[:200]

            # Comparison
            if visual_type == "comparison":
                columns = visual.get("columns")
                comparisons = visual.get("comparisons")

                if (
                    not isinstance(columns, list)
                    or len(columns) < 2
                    or not isinstance(comparisons, list)
                    or not comparisons
                ):
                    return []

                for row in comparisons:
                    if (
                        not isinstance(row, dict)
                        or not isinstance(row.get("label"), str)
                        or not isinstance(row.get("values"), list)
                        or len(row["values"]) != len(columns)
                        or any(not isinstance(v, str) for v in row["values"])
                    ):
                        return []

                return [visual]

            # Steps
            if visual_type == "steps":
                steps = visual.get("steps")

                if (
                    not isinstance(steps, list)
                    or not steps
                    or any(
                        not isinstance(step, dict)
                        or not isinstance(step.get("title"), str)
                        for step in steps
                    )
                ):
                    return []

                return [visual]

            # Timeline
            if visual_type == "timeline":
                timeline = visual.get("timeline")

                if (
                    not isinstance(timeline, list)
                    or not timeline
                    or any(
                        not isinstance(event, dict)
                        or not isinstance(event.get("title"), str)
                        for event in timeline
                    )
                ):
                    return []

                return [visual]

            # Data chart
            if visual_type == "data_chart":
                chart = visual.get("chart")

                if not isinstance(chart, dict):
                    return []

                labels = chart.get("labels")
                series = chart.get("series")

                if (
                    not isinstance(labels, list)
                    or not labels
                    or not isinstance(series, list)
                    or not series
                ):
                    return []

                for item in series:
                    if (
                        not isinstance(item, dict)
                        or not isinstance(item.get("values"), list)
                        or len(item["values"]) != len(labels)
                        or any(
                            not isinstance(value, (int, float))
                            or isinstance(value, bool)
                            for value in item["values"]
                        )
                    ):
                        return []

                return [visual]

            # Graph-based visual types
            graph_types = {
                "flowchart",
                "concept_map",
                "system_architecture",
                "connection_graph",
                "hierarchy",
                "decision_tree",
                "cycle",
                "mind_map",
                "blueprint",
            }

            if visual_type in graph_types:
                nodes = visual.get("nodes")
                edges = visual.get("edges")

                if not isinstance(nodes, list) or not nodes:
                    return []

                if not isinstance(edges, list):
                    return []

                valid_node_ids = set()

                for node in nodes:
                    if not isinstance(node, dict):
                        return []

                    node_id = node.get("id")
                    label = node.get("label")
                    color = node.get("color")

                    if (
                        not isinstance(node_id, str)
                        or not node_id.strip()
                        or node_id in valid_node_ids
                        or not isinstance(label, str)
                        or not label.strip()
                        or not isinstance(color, str)
                    ):
                        return []

                    valid_node_ids.add(node_id)

                for edge in edges:
                    if not isinstance(edge, dict):
                        return []

                    source = edge.get("from")
                    target = edge.get("to")

                    if (
                        not isinstance(source, str)
                        or not isinstance(target, str)
                        or source not in valid_node_ids
                        or target not in valid_node_ids
                        or source == target
                    ):
                        return []

                if visual_type == "mind_map":
                    center_id = visual.get("centerNodeId")

                    if center_id is not None and center_id not in valid_node_ids:
                        return []

                if visual_type == "hierarchy":
                    for node in nodes:
                        parent_id = node.get("parentId")
                        if parent_id is not None and parent_id not in valid_node_ids:
                            return []

                visual["nodes"] = nodes
                visual["edges"] = edges

                return [visual]

            return []

        except Exception as exc:
            print(f"[VISUAL SERVICE ERROR] {exc}")
            return []