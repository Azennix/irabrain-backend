from __future__ import annotations

from typing import Any
from uuid import uuid4


# ============================================================
# RESPONSE BLOCK ID
# ============================================================

def _generate_block_id() -> str:
    """Generate a unique identifier for each response block."""
    return f"block_{uuid4().hex}"


# ============================================================
# TEXT BLOCK
# ============================================================

def make_text_block(
    content: str,
    block_id: str | None = None,
) -> dict[str, Any] | None:
    """
    Create a text response block.

    Empty or invalid text is ignored.
    Original text content is preserved.
    """

    if not isinstance(content, str):
        return None

    if not content.strip():
        return None

    return {
        "id": block_id or _generate_block_id(),
        "type": "text",
        "content": content,
    }


# ============================================================
# VISUAL BLOCK
# ============================================================

def make_visual_block(
    visual: dict[str, Any],
    block_id: str | None = None,
) -> dict[str, Any] | None:
    """
    Create a visual response block.

    Visual payload validation is primarily handled
    by VisualIntelligenceService.
    """

    if not isinstance(visual, dict):
        return None

    if visual.get("type") in (None, "none"):
        return None

    return {
        "id": block_id or _generate_block_id(),
        "type": "visual",
        "visual": visual,
    }


# ============================================================
# RESPONSE BLOCK NORMALIZATION
# ============================================================

def normalize_response_blocks(
    blocks: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """
    Normalize blocks into the canonical IRA Response V2 format.

    Supported block types:
        - text
        - visual

    The original block order is preserved.
    """

    normalized: list[dict[str, Any]] = []

    if not isinstance(blocks, list):
        blocks = []

    for block in blocks:

        if not isinstance(block, dict):
            continue

        block_type = block.get("type")

        if block_type == "text":

            normalized_block = make_text_block(
                content=block.get("content"),
                block_id=block.get("id"),
            )

            if normalized_block:
                normalized.append(normalized_block)

        elif block_type == "visual":

            normalized_block = make_visual_block(
                visual=block.get("visual"),
                block_id=block.get("id"),
            )

            if normalized_block:
                normalized.append(normalized_block)

    return {
        "version": 2,
        "blocks": normalized,
    }


# ============================================================
# EXTRACT TEXT
# ============================================================

def extract_text_content(
    response_blocks: dict[str, Any],
) -> str:
    """
    Extract all text blocks in their original order.

    Used for backward compatibility with existing
    content-based clients and database fields.
    """

    if not isinstance(response_blocks, dict):
        return ""

    blocks = response_blocks.get("blocks", [])

    if not isinstance(blocks, list):
        return ""

    text_parts: list[str] = []

    for block in blocks:

        if not isinstance(block, dict):
            continue

        if block.get("type") != "text":
            continue

        content = block.get("content")

        if isinstance(content, str):
            text_parts.append(content)

    return "".join(text_parts)


# ============================================================
# EXTRACT LEGACY VISUAL DATA
# ============================================================

def extract_visual_data(
    response_blocks: dict[str, Any],
) -> list[dict[str, Any]] | None:
    """
    Extract visual payloads for existing clients
    and database compatibility.
    """

    if not isinstance(response_blocks, dict):
        return None

    blocks = response_blocks.get("blocks", [])

    if not isinstance(blocks, list):
        return None

    visuals: list[dict[str, Any]] = []

    for block in blocks:

        if not isinstance(block, dict):
            continue

        if block.get("type") != "visual":
            continue

        visual = block.get("visual")

        if isinstance(visual, dict):
            visuals.append(visual)

    return visuals or None


# ============================================================
# BUILD COMPLETE RESPONSE
# ============================================================

def build_response_payload(
    text: str = "",
    visuals: list[dict[str, Any]] | None = None,
    blocks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Build the complete IRA Response V2 payload.

    If explicit ordered blocks are supplied, their order
    is preserved.

    Otherwise, a compatibility response is constructed
    using the existing text-then-visual generation flow.

    Returns:
        response_blocks
        content
        visual_data
    """

    if blocks is not None:

        response_blocks = normalize_response_blocks(blocks)

    else:

        generated_blocks: list[dict[str, Any]] = []

        text_block = make_text_block(text)

        if text_block:
            generated_blocks.append(text_block)

        if isinstance(visuals, list):

            for visual in visuals:

                visual_block = make_visual_block(visual)

                if visual_block:
                    generated_blocks.append(visual_block)

        response_blocks = normalize_response_blocks(
            generated_blocks
        )

    return {
        "response_blocks": response_blocks,
        "content": extract_text_content(response_blocks),
        "visual_data": extract_visual_data(response_blocks),
    }
