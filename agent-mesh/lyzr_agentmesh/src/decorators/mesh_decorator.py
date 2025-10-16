"""
AgentMesh Decorator for Auto-Publishing

Provides @publish_to_mesh decorator to simplify agent integration by automatically
publishing function calls to the mesh with minimal boilerplate.
"""

import functools
import inspect
from typing import Any, List, Union, Optional


def publish_to_mesh(
    observation: str,
    tags: List[str],
    insight_type: str = "observation",
    context: Union[bool, List[str]] = True,
    builds_on: Optional[str] = None,
    led_to_by: Optional[str] = None
):
    """
    Decorator that automatically publishes function calls to AgentMesh.

    Args:
        observation: Template string with {param} placeholders
            Example: "{count} customers inquired about {product}"

        tags: List of tag templates with {param} placeholders or list expansion
            Examples:
            - ["inquiry", "{product}"]  # Template substitution
            - ["{tags}"]                 # List expansion from parameter

        insight_type: Type of insight (observation, pattern, decision, action)
            Default: "observation"

        context: Context capture strategy
            - True: Capture all function parameters (default)
            - False: No context
            - List[str]: Capture only specified parameters
            Example: ["product", "count"]

        builds_on: Parameter name containing insight ID(s) this insight builds on
            - Creates BUILDS_ON relationship(s) automatically
            - Supports single insight ID or list of IDs
            Example: "related_insights"

        led_to_by: Parameter name containing insight ID(s) that led to this insight
            - Creates LED_TO relationship(s) automatically
            - Supports single insight ID or list of IDs
            - Special value "result": Use function's return value as insight ID(s)
            Example: "previous_insights" or "result"

    Returns:
        Decorated function that auto-publishes to mesh and returns insight ID

    Usage:
        @publish_to_mesh(
            observation="{count} customers inquired about {product}",
            tags=["inquiry", "{product}"],
            insight_type="observation",
            context=["product", "count"],
            builds_on="related_insights"
        )
        def log_inquiry(self, product, count, related_insights=None):
            # Your logic here (or just pass)
            pass

    The decorator will:
        1. Capture function parameters
        2. Run the original function
        3. Substitute {param} templates with actual values
        4. Expand list parameters (e.g., "{tags}" -> ["tag1", "tag2"])
        5. Build context dictionary based on context parameter
        6. Publish insight to mesh via self.adapter.publish_insight()
        7. Create BUILDS_ON relationships if builds_on is specified
        8. Create LED_TO relationships if led_to_by is specified
        9. Return insight ID
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Step 1: Get function parameters
            sig = inspect.signature(func)
            bound = sig.bind(self, *args, **kwargs)
            bound.apply_defaults()
            params = {k: v for k, v in bound.arguments.items() if k != 'self'}

            # Step 2: Run original function
            result = func(self, *args, **kwargs)

            # Step 3: Substitute templates in observation
            obs = observation.format(**params)

            # Step 4: Substitute templates in tags (with list expansion support)
            resolved_tags = []
            for tag in tags:
                if tag.startswith("{") and tag.endswith("}"):
                    # It's a parameter reference like "{tags}" or "{product}"
                    param_name = tag[1:-1]
                    param_value = params.get(param_name)
                    if isinstance(param_value, list):
                        # Expand the list (flatten)
                        resolved_tags.extend([str(t).lower() for t in param_value])
                    else:
                        # Single value
                        resolved_tags.append(str(param_value).lower())
                else:
                    # Normal template or literal string
                    resolved_tags.append(tag.format(**params).lower())

            # Step 5: Build context based on context parameter
            if context is True:
                # Capture all parameters
                insight_context = params.copy()
            elif isinstance(context, list):
                # Capture only specified parameters
                insight_context = {k: params[k] for k in context if k in params}
            else:
                # No context
                insight_context = {}

            # Step 6: Publish insight to mesh
            if not hasattr(self, 'adapter'):
                raise AttributeError(
                    f"Object {self} must have 'adapter' attribute (AgentMeshAdapter) "
                    "to use @publish_to_mesh decorator"
                )

            new_insight_id = self.adapter.publish_insight(
                observation=obs,
                tags=resolved_tags,
                context=insight_context,
                insight_type=insight_type
            )

            # Step 7: Create BUILDS_ON relationships
            if builds_on:
                insight_ids = _get_insight_ids(params, builds_on)
                for target_id in insight_ids:
                    self.adapter.add_relationship(
                        source_id=new_insight_id,
                        target_id=target_id,
                        relation_type="BUILDS_ON"
                    )

            # Step 8: Create LED_TO relationships
            if led_to_by:
                if led_to_by == "result":
                    # Use function return value as insight ID(s)
                    insight_ids = _ensure_list(result)
                else:
                    # Use parameter value as insight ID(s)
                    insight_ids = _get_insight_ids(params, led_to_by)

                for source_id in insight_ids:
                    self.adapter.add_relationship(
                        source_id=source_id,
                        target_id=new_insight_id,
                        relation_type="LED_TO"
                    )

            # Step 9: Return insight ID
            return new_insight_id

        return wrapper
    return decorator


def _get_insight_ids(params: dict, param_name: str) -> List[str]:
    """
    Extract insight IDs from a parameter.

    Args:
        params: Dictionary of function parameters
        param_name: Name of parameter containing insight ID(s)

    Returns:
        List of insight IDs (empty list if parameter is None or missing)
    """
    value = params.get(param_name)
    if value is None:
        return []
    return _ensure_list(value)


def _ensure_list(value: Any) -> List[Any]:
    """
    Ensure value is a list.

    Args:
        value: Single value or list of values

    Returns:
        List containing value(s)
    """
    if isinstance(value, list):
        return value
    elif value:
        return [value]
    return []
