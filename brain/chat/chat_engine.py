from brain.engine.engine import Engine
from brain.llm.chat_prompt_builder import ChatPromptBuilder
from brain.chat.response_validator import ResponseValidator
from brain.chat.confidence_controller import ConfidenceController
from brain.llm.llm_request_context import LLMRequestContext

class ChatEngine(Engine):

    def __init__(
        self,
        llm_service
    ):
        self.llm_service = llm_service

        self.response_validator = (
            ResponseValidator()
        )

        self.confidence_controller = (
            ConfidenceController()
        )

    # =====================================================
    # NORMAL RESPONSE
    # Existing pipeline
    # =====================================================

    def execute(
        self,
        request,
        context,
        conversation_history=None,
        reasoning_result=None,
        tool_result=None,
        language_policy=None
    ):

        prompt = ChatPromptBuilder.build(
            user_message=request.query,
            context=context,
            conversation_history=conversation_history,
            reasoning_result=reasoning_result,
            tool_result=tool_result,
            language_policy=language_policy,
            attachments=request.attachments,
            workspace_mode=request.metadata.get(
               "workspace_mode",
               "personal",
    ),
)

        llm_response = self.llm_service.generate(
             prompt
)

        response = llm_response.content

        response = (
            self.response_validator.validate(
                response
            )
        )

        confidence = 1.0

        if reasoning_result is not None:
            confidence = (
                reasoning_result.confidence
            )

        response = (
            self.confidence_controller.adjust(
                response=response,
                confidence=confidence
            )
        )

        print(
            "\n========== IRABRAIN =========="
        )

        print(response)

        print(
            "=============================="
        )

        return response

    # =====================================================
    # STREAMING RESPONSE
    # Final IRA answer only
    # =====================================================

    def execute_stream(
        self,
        request,
        context,
        conversation_history=None,
        reasoning_result=None,
        tool_result=None,
        language_policy=None,
        brain_tier=None,
    ):

        prompt = ChatPromptBuilder.build(
            user_message=request.query,
            context=context,
            conversation_history=conversation_history,
            reasoning_result=reasoning_result,
            tool_result=tool_result,
            language_policy=language_policy,
            attachments=request.attachments,
            workspace_mode=request.metadata.get(
             "workspace_mode",
             "personal"
),
        )

        request_context = LLMRequestContext(
            request_id=request.request_id,
            user_id=request.user_id,
            brain_tier=brain_tier,
        )

        # Keep complete response locally.
        full_response = ""



        # Stream chunks from the configured LLM provider.
        for chunk in self.llm_service.generate_stream(
            prompt,
            request_context=request_context,
        ):



            full_response += chunk

            # Send chunk to caller immediately.
            yield chunk

        # Validate complete response after streaming.
        validated_response = (
            self.response_validator.validate(
                full_response
            )
        )

        confidence = 1.0

        if reasoning_result is not None:
            confidence = (
                reasoning_result.confidence
            )

        final_response = (
            self.confidence_controller.adjust(
                response=validated_response,
                confidence=confidence
            )
        )

        print(
            "\n========== IRABRAIN STREAM COMPLETE =========="
        )

        print(final_response)

        print(
            "=============================================="
        )
    def generate_visual(
        self,
        *,
        user_message: str,
        assistant_response: str,
        request_context: LLMRequestContext,
    ) -> dict | None:
        """Generate a validated, answer-grounded visual payload."""

        visual_types = {
            "concept_map",
            "flowchart",
            "comparison",
            "steps",
            "system_architecture",
            "connection_graph",
            "hierarchy",
            "decision_tree",
            "cycle",
            "timeline",
            "data_chart",
        }

        prompt = f"""
Create one useful visual representation of the assistant answer.

USER QUESTION:
{user_message}

ASSISTANT ANSWER:
{assistant_response}


COLOR RULES - FOR POWER FEEL:

For EACH node, add "color" field based on situation:
- DANGER / ERROR / FAILURE / CRITICAL / RISK / WARNING / BLOCKED / ATTACK: "bg-[#000000] border-[#8A0303]/70 text-[#EEE3D1]" -> BLOOD RED
- DECISION / APPROVAL / HUMAN-LOOP / REVIEW / CHECKPOINT: "bg-[#171614] border-[#EEE3D1]/40 text-[#EEE3D1]" -> BRIGHT
- NORMAL / SUCCESS / DEFAULT: "bg-[#171614] border-[#EEE3D1]/25 text-[#EEE3D1]" -> NORMAL
- START / GOAL / INPUT: "bg-[#000000] border-[#8A0303]/50 text-[#EEE3D1]" -> POWER START
Choose type: concept_map, flowchart, comparison, steps
Return JSON object with fields: type, title, description, nodes (with id, label, description, color), edges, steps, columns, comparisons


Choose the single most suitable type:
- concept_map: one central idea connected to related concepts.
- flowchart: sequential process with directional connections.
- comparison: compare two or more options using matching criteria.
- steps: an ordered procedure.
- system_architecture: components arranged in meaningful layers.
- connection_graph: a network of related entities and relationships.
- hierarchy: parent-child structure using parentId.
- decision_tree: a question or choice with branches and outcomes.
- cycle: stages that repeat in a loop.
- timeline: events arranged chronologically.
- data_chart: numeric values explicitly supported by the answer.

Return JSON only, using this schema:
{{
  "type": "one supported type, or none",
  "title": "short title",
  "description": "optional concise explanation",
  "nodes": [
    {{
      "id": "unique_id",
      "label": "short label",
      "description": "optional",
      "parentId": "optional parent node id",
      "group": "optional group",
      "layer": "optional layer"
    }}
  ],
  "edges": [
    {{
      "from": "existing node id",
      "to": "existing node id",
      "label": "optional relationship",
      "type": "directed"
    }}
  ],
  "steps": [
    {{"title": "step", "description": "optional"}}
  ],
  "columns": ["comparison option names"],
  "comparisons": [
    {{"label": "criterion", "values": ["value per option"]}}
  ],
  "timeline": [
    {{"title": "event", "date": "supported date", "description": "optional"}}
  ],
  "chart": {{
    "labels": ["category"],
    "series": [
      {{"name": "series name", "values": [1.0]}}
    ],
    "unit": "optional"
  }},
  "branches": [
    {{"from": "existing node id", "label": "choice", "to": "existing node id"}}
  ],
  "centerNodeId": "optional existing node id",
  "metadata": {{
    "complexity": "simple",
    "layout": "vertical",
    "source": "answer"
  }}
}}

Rules:
- Choose the type based on the user's actual question and answer, not randomly.
- Only use facts supported by the assistant answer.
- Never invent numeric data, dates, relationships, or outcomes.
- Use concise labels and avoid duplicating the full answer.
- Every edge endpoint must refer to a node that exists.
- For hierarchy, use parentId to express parent-child relationships.
- For decision_tree, provide nodes and directed branch edges with meaningful labels.
- For cycle, order nodes according to the cycle stages and connect the last stage back to the first when appropriate.
- For timeline, use only supported events and dates.
- For data_chart, use only real numeric values present in the answer.
- For comparison, align each row's values with the columns in the same order.
# prompt lo comparison section ki kindha add chey:

For comparison type CRITICAL RULE:
- columns: ONLY the POVs/options being compared, e.g. ["Developer POV", "User POV"]
- DO NOT include "Stage", "Step", "Phase", "Aspect" in columns - that goes in label field
- comparisons: [{"label":"Goal","values":["Parse intent...","I want this done"]}] -> values length MUST EQUAL columns length

WRONG: columns=["Stage","Developer POV","User POV"], values=["Parse...","I want...","-"]
RIGHT: columns=["Developer POV","User POV"], values=["Parse intent, constraints, permissions","I want this done"]

- If a visual adds little value or the answer lacks sufficient structure, return {{"type":"none"}}.
- Return valid JSON only, without Markdown fences.
"""

        try:
            visual = self.llm_service.generate_structured(
                prompt,
                request_context=request_context,
                temperature=0.0,
            )

            if not isinstance(visual, dict):
                return None

            visual_type = visual.get("type")

            if visual_type == "none":
                return None

            if visual_type not in visual_types:
                return None

            title = visual.get("title")
            if not isinstance(title, str) or not title.strip():
                return None

            visual["title"] = title.strip()[:200]

            if "description" in visual and not isinstance(
                visual["description"], str
            ):
                visual.pop("description", None)

            nodes = visual.get("nodes", [])
            edges = visual.get("edges", [])
            if not isinstance(nodes, list) or not isinstance(edges, list):
                return None

            valid_node_ids = {
                node.get("id")
                for node in nodes
                if isinstance(node, dict)
                and isinstance(node.get("id"), str)
            }

            if any(
                not isinstance(edge, dict)
                or edge.get("from") not in valid_node_ids
                or edge.get("to") not in valid_node_ids
                for edge in edges
            ):
                return None

            if visual_type == "comparison":
                if (
                    not isinstance(visual.get("columns"), list)
                    or not isinstance(visual.get("comparisons"), list)
                    or not visual["columns"]
                    or not visual["comparisons"]
                ):
                    return None

            if visual_type == "timeline":
                if not isinstance(visual.get("timeline"), list) or not visual["timeline"]:
                    return None

            if visual_type == "data_chart":
                chart = visual.get("chart")
                if not isinstance(chart, dict):
                    return None

                labels = chart.get("labels")
                series = chart.get("series")

                if (
                    not isinstance(labels, list)
                    or not isinstance(series, list)
                    or not labels
                    or not series
                ):
                    return None

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
                        return None

            if visual_type in {
                "concept_map",
                "flowchart",
                "system_architecture",
                "connection_graph",
                "hierarchy",
                "decision_tree",
                "cycle",
            } and not nodes:
                return None

            if visual_type == "steps":
                if not isinstance(visual.get("steps"), list) or not visual["steps"]:
                    return None

            return visual

        except Exception as error:
            print(
                "[VISUAL INTELLIGENCE] Generation failed:",
                str(error),
            )
            return None


    def generate_visuals(
        self,
        *,
        user_message: str,
        assistant_response: str,
        request_context: LLMRequestContext,
        visual_type_hint: str | None = None,
    ) -> list[dict] | None:

        preferred = visual_type_hint or "choose the best fit" 


        prompt = f"""
    You are IRABRAIN's Visual Intelligence Engine.

    Your responsibility is to decide whether the current conversation
    benefits from a visual representation and, if so, create the single
    most useful visual for the user's intent.

    Do not generate visuals merely because you can.
    Think about what would help the user understand, decide, build,
    debug, compare, or execute something.

    USER MESSAGE:
    {user_message}

    IRABRAIN RESPONSE:
    {assistant_response[:4000]}

==================================================
1. INTELLIGENT VISUAL DECISION
==================================================

First understand the user's intent, the complexity of the subject,
the structure of the answer, and whether a visual would provide
meaningful value beyond the text.

Possible decisions:

- No visual: a visual would add little value.
- Process visualization: the user needs to understand a sequence,
  workflow, algorithm, or execution process.
- System visualization: the user needs to understand architecture,
  components, integrations, dependencies, or data flow.
- Concept visualization: the user needs to understand relationships
  between concepts, entities, or ideas.
- Comparative visualization: the user needs to compare alternatives.
- Hierarchical visualization: the user needs to understand levels,
  ownership, decomposition, or parent-child relationships.
- Temporal visualization: the user needs to understand events or
  stages over time.
- Quantitative visualization: the answer contains sufficient
  supported numerical data to justify a chart.

These are reasoning possibilities, not mandatory categories.

Use your judgment. Do not follow keyword-based rules.
A short question may deserve a visual, and a long answer may not.

Do not create a visual just to decorate the response.
Do not invent information absent from the user's message or answer.
Do not create a diagram if the relationships cannot be represented
accurately from the available information.

==================================================
2. ONE COHERENT VISUAL
==================================================

Return AT MOST ONE visual object.

If the subject is complex, represent its complexity INSIDE that
single visual using multiple connected nodes, edges, meaningful
groups, and clear relationships.

Examples of good decisions:

- A greeting: no visual.
- A simple definition: usually no visual.
- A programming algorithm: one flowchart when useful.
- An MVP: one coherent architecture or workflow diagram.
- A connected AI system: one system architecture with components
  and relationships.
- A comparison: one comparison visual.
- A multi-stage process: one flowchart or steps visual.
- A complex topic with several subcomponents: one integrated diagram,
  not separate diagrams for each perspective.

Never produce multiple visual cards, developer/user POV variants,
or alternative diagrams for the same answer.

The goal is one useful visual, not the maximum number of visuals.

==================================================
3. SELECT THE BEST REPRESENTATION
==================================================

PREFERRED TYPE: {preferred}

Use the preferred type unless the answer clearly cannot be
represented that way. Use flowchart ONLY for sequential
processes. Do not fall back to flowchart for comparisons,
architectures, relationships, trends or numbers.

Allowed types:
- flowchart
- concept_map
- steps
- comparison
- hierarchy
- cycle
- timeline
- system_architecture
- connection_graph
- decision_tree
- data_chart

Use the type that best expresses the relationships in the answer.
Do not choose a type merely because it appears in this list.

==================================================
4. NODE AND EDGE QUALITY
==================================================

When a visual is appropriate:

- Give it a concise, descriptive title.
- Use meaningful, specific node labels.
- Represent relationships accurately.
- Give every node a unique ID.
- Use edges that reference existing node IDs.
- Keep labels concise and readable.
- Include enough nodes to explain the subject without unnecessary
  complexity.
- Use connected nodes where relationships matter.
- Avoid disconnected decorative nodes.
- Avoid duplicate nodes and redundant edges.
- Include descriptions only when they improve understanding.
- Do not invent components, execution stages, metrics, or outcomes.
- Preserve important dependencies and decision branches.

For a software architecture, represent actual components and their
interactions, such as frontend, API, services, database, and external
integrations, but include only those supported by the answer.

For an algorithm or workflow, represent the real sequence and
decision branches.

For a comparison, ensure the compared dimensions are consistent.

For a data chart, use only numerical values supported by the answer.

==================================================
5. VISUAL DESIGN SYSTEM
==================================================

Follow IRABRAIN's visual palette:

- Background: #000000
- Primary text: #EEE3D1
- Dark node background: #171614
- Blood-red accent: #8A0303

Every node must include a "color" field.

Use these styles according to meaning:

Normal process, information, or success:
"bg-[#171614] border-[#EEE3D1]/25 text-[#EEE3D1]"

Decision, review, approval, or human checkpoint:
"bg-[#171614] border-[#EEE3D1]/40 text-[#EEE3D1]"

Input, starting point, or goal:
"bg-[#000000] border-[#8A0303]/50 text-[#EEE3D1]"

Danger, failure, risk, or critical issue:
"bg-[#000000] border-[#8A0303]/70 text-[#EEE3D1]"

Use blood red sparingly and only where semantically appropriate.
Do not color ordinary nodes as dangerous just for visual impact.

==================================================
6. OUTPUT CONTRACT
==================================================

Return valid JSON only. Do not use Markdown fences.

When no visual is useful, return exactly:
{{"type": "none"}}

When a visual is useful, return one JSON object with this structure:

{{
  "type": "flowchart",
  "title": "Request Processing Workflow",
  "description": "How the request moves through the system",
  "nodes": [
    {{
      "id": "input",
      "label": "User Request",
      "description": "Incoming request",
      "color": "bg-[#000000] border-[#8A0303]/50 text-[#EEE3D1]"
    }},
    {{
      "id": "process",
      "label": "Process Request",
      "description": "Validate and execute",
      "color": "bg-[#171614] border-[#EEE3D1]/25 text-[#EEE3D1]"
    }}
  ],
  "edges": [
    {{
      "from": "input",
      "to": "process"
    }}
  ]
}}

PREFERRED TYPE: {preferred}

Use the preferred type unless the answer clearly cannot be
represented that way. Use flowchart ONLY for sequential
processes. Do not fall back to flowchart for comparisons,
architectures, relationships, trends or numbers.

The example illustrates the schema only. Generate content relevant
to the actual user message and answer.

Do not return an array of different visual perspectives.
Do not return multiple visual objects.
"""

        try:
            visuals = self.llm_service.generate_structured(
                prompt,
                request_context=request_context,
                temperature=0.0,
        )

            if isinstance(visuals, dict) and "visuals" in visuals:
                visuals = visuals["visuals"]

        # Support providers that return a one-item list despite
        # being instructed to return a single object.
            if isinstance(visuals, list):
                if len(visuals) != 1:
                    print(
                    "[VISUAL INTELLIGENCE] Expected one visual; "
                    f"received {len(visuals)}."
                )
                    return None

                visuals = visuals[0]

            if not isinstance(visuals, dict):
                return None

            if visuals.get("type") == "none":
                return None

            allowed_types = {
            "concept_map",
            "flowchart",
            "comparison",
            "steps",
            "hierarchy",
            "cycle",
            "timeline",
            "system_architecture",
            "connection_graph",
            "decision_tree",
            "data_chart",
            }

            vtype = visuals.get("type")
            if vtype not in allowed_types:
                return None

            title = visuals.get("title")
            if not isinstance(title, str) or not title.strip():
                return None
            visuals["title"] = title.strip()[:200]

            node_types = {
                "flowchart", "concept_map", "system_architecture",
                "connection_graph", "hierarchy", "decision_tree", "cycle",
            }

            if vtype in node_types:
                nodes = visuals.get("nodes")
                edges = visuals.get("edges", [])
                if not isinstance(nodes, list) or not nodes:
                    return None
                if not isinstance(edges, list):
                    edges = []

                valid_nodes, node_ids = [], set()
                for node in nodes:
                    if not isinstance(node, dict):
                        continue
                    nid, label = node.get("id"), node.get("label")
                    if not isinstance(nid, str) or not nid.strip() or nid in node_ids:
                        continue
                    if not isinstance(label, str) or not label.strip():
                        continue
                    if not isinstance(node.get("color"), str):
                        node["color"] = "bg-[#171614] border-[#EEE3D1]/25 text-[#EEE3D1]"
                    node_ids.add(nid)
                    valid_nodes.append(node)
                if not valid_nodes:
                    return None

                visuals["nodes"] = valid_nodes
                visuals["edges"] = [
                    e for e in edges
                    if isinstance(e, dict)
                    and e.get("from") in node_ids
                    and e.get("to") in node_ids
                    and e.get("from") != e.get("to")
                ]

            elif vtype == "comparison":
                cols, comps = visuals.get("columns"), visuals.get("comparisons")
                if not isinstance(cols, list) or not isinstance(comps, list) or not cols or not comps:
                    return None

            elif vtype == "timeline":
                if not isinstance(visuals.get("timeline"), list) or not visuals["timeline"]:
                    return None

            elif vtype == "steps":
                if not isinstance(visuals.get("steps"), list) or not visuals["steps"]:
                    return None

            elif vtype == "data_chart":
                chart = visuals.get("chart")
                if not isinstance(chart, dict):
                    return None
                labels, series = chart.get("labels"), chart.get("series")
                if not isinstance(labels, list) or not isinstance(series, list) or not labels or not series:
                    return None
                for s in series:
                    vals = s.get("values") if isinstance(s, dict) else None
                    if (not isinstance(vals, list) or len(vals) != len(labels)
                            or any(not isinstance(x, (int, float)) or isinstance(x, bool) for x in vals)):
                        return None
                if chart.get("kind") not in ("bar", "line", "pie"):
                    chart["kind"] = "bar"

            return [visuals]

        except Exception as error:
            print(
               "[VISUAL INTELLIGENCE] Generation failed:",
                 str(error),
        )
            return None
