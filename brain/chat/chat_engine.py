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
    ) -> list[dict] | None:

        prompt = f"""
Create 2-4 DIFFERENT visual POVs for the answer.

USER QUESTION:
{user_message}

ASSISTANT ANSWER:
{assistant_response[:3000]}

TASK: Based on user POV, generate multiple visuals.

COLOR RULES - CRITICAL FOR POWER FEEL:
For EACH node, add "color" field based on situation:

- DANGER / WARNING / RISK / FAILURE / ERROR / CRITICAL / BLOCKED / ATTACK / BUG / VULNERABILITY / CRASH:
  "color": "bg-[#000000] border-[#8A0303]/70 text-[#EEE3D1]"  -> BLOOD RED border, black bg

- DECISION / BRANCH / APPROVAL / HUMAN-LOOP / GATE / REVIEW / CHECKPOINT:
  "color": "bg-[#171614] border-[#EEE3D1]/40 text-[#EEE3D1]"  -> BRIGHT EEE3D1 border

- NORMAL / SUCCESS / PROCESS / STEP / DEFAULT:
  "color": "bg-[#171614] border-[#EEE3D1]/25 text-[#EEE3D1]"  -> NORMAL

- START / GOAL / TRIGGER / INPUT:
  "color": "bg-[#000000] border-[#8A0303]/50 text-[#EEE3D1]"  -> Slight blood red for power

Examples:
  {{"id":"1","label":"User Input","color":"bg-[#000000] border-[#8A0303]/50 text-[#EEE3D1]"}}
  {{"id":"2","label":"Validate Request","description":"Check auth","color":"bg-[#171614] border-[#EEE3D1]/25 text-[#EEE3D1]"}}
  {{"id":"3","label":"Risk Detected!","description":"SQL Injection","color":"bg-[#000000] border-[#8A0303]/70 text-[#EEE3D1]"}}
  {{"id":"4","label":"Human Approval Needed","color":"bg-[#171614] border-[#EEE3D1]/40 text-[#EEE3D1]"}}

VISUAL TYPES:
- flowchart: process or sequence
- concept_map: connected concepts
- steps: ordered explanation
- comparison: differences
- hierarchy: parent-child
- cycle: loop
- timeline: events

Return JSON ARRAY ONLY:
[
  {{"type":"flowchart","title":"Overall Flow","nodes":[{{"id":"1","label":"Goal","color":"bg-[#000000] border-[#8A0303]/50 text-[#EEE3D1]"}}],"edges":[{{"from":"1","to":"2"}}]}},
  {{"type":"concept_map","title":"Developer POV - Roles","nodes":[{{"id":"p1","label":"Planner","color":"bg-[#171614] border-[#EEE3D1]/25 text-[#EEE3D1]"}}],"edges":[{{"from":"p1","to":"r1"}}]}}
]

Allowed types: flowchart, concept_map, steps, comparison, hierarchy, cycle, timeline, system_architecture
If no visual needed, return [{{"type":"none"}}]
"""

        try:
            visuals = self.llm_service.generate_structured(
                prompt,
                temperature=0.2,
            )
            if isinstance(visuals, dict) and "visuals" in visuals:
                visuals = visuals["visuals"]
            if isinstance(visuals, dict):
                visuals = [visuals]
            if not isinstance(visuals, list):
                return None

            cleaned = []
            for v in visuals:
                if not isinstance(v, dict): continue
                if v.get("type") == "none": continue
                if v.get("type") not in {"concept_map","flowchart","comparison","steps","hierarchy","cycle","timeline","system_architecture","connection_graph","decision_tree","data_chart"}:
                    continue
                if not isinstance(v.get("title"), str): continue
                v["title"] = v["title"][:200]
                cleaned.append(v)

            return cleaned[:4] if cleaned else None

        except Exception as e:
            print("[VISUAL MULTI] failed:", e)
            return None
