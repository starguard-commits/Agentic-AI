"""
Permission management for AgentMesh.

Handles access control and filtering based on agent roles and permissions.
"""

from typing import List, Dict, Any, Optional


class PermissionManager:
    """
    Manages permissions and access control in the mesh.

    Implements role-based access control where:
    - Each insight has a list of allowed roles
    - Queries are filtered based on requester's role
    """

    def __init__(self):
        """Initialize the permission manager."""
        # Could be extended with more complex rules
        self.permission_rules = {}

    def can_access(self, item: Dict[str, Any], requester_role: str) -> bool:
        """
        Check if a requester can access an item.

        Args:
            item: Item (insight, agent, etc.) with permissions
            requester_role: Role of the requester

        Returns:
            True if access is granted, False otherwise
        """
        # Get permissions list from item
        permissions = item.get("permissions", [])

        # If no permissions specified, deny by default (secure by default)
        if not permissions:
            return False

        # Check if requester's role is in allowed permissions
        return requester_role in permissions

    def filter_by_permissions(
        self,
        items: List[Dict[str, Any]],
        requester_role: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter a list of items by permissions.

        Args:
            items: List of items to filter
            requester_role: Role of the requester (None = no filtering)

        Returns:
            Filtered list of items
        """
        # If no role specified, return all (admin/system access)
        if requester_role is None:
            return items

        # Filter items where requester has access
        return [
            item for item in items
            if self.can_access(item, requester_role)
        ]

    def validate_permissions(self, permissions: List[str]) -> bool:
        """
        Validate a permissions list.

        Args:
            permissions: List of roles/permissions

        Returns:
            True if valid, False otherwise
        """
        # Basic validation - ensure it's a list of strings
        if not isinstance(permissions, list):
            return False

        for perm in permissions:
            if not isinstance(perm, str):
                return False

        return True

    def merge_permissions(
        self,
        perm_list1: List[str],
        perm_list2: List[str]
    ) -> List[str]:
        """
        Merge two permission lists (union).

        Args:
            perm_list1: First permissions list
            perm_list2: Second permissions list

        Returns:
            Merged list with unique permissions
        """
        return list(set(perm_list1) | set(perm_list2))

    def intersect_permissions(
        self,
        perm_list1: List[str],
        perm_list2: List[str]
    ) -> List[str]:
        """
        Intersect two permission lists (common permissions).

        Args:
            perm_list1: First permissions list
            perm_list2: Second permissions list

        Returns:
            List of common permissions
        """
        return list(set(perm_list1) & set(perm_list2))

    def add_permission_rule(
        self,
        rule_name: str,
        rule_func: callable
    ) -> None:
        """
        Add a custom permission rule.

        Args:
            rule_name: Name of the rule
            rule_func: Function that takes (item, requester_role) and returns bool
        """
        self.permission_rules[rule_name] = rule_func

    def check_custom_rule(
        self,
        rule_name: str,
        item: Dict[str, Any],
        requester_role: str
    ) -> bool:
        """
        Check a custom permission rule.

        Args:
            rule_name: Name of the rule to check
            item: Item to check
            requester_role: Role of requester

        Returns:
            Result of custom rule, or False if rule doesn't exist
        """
        if rule_name in self.permission_rules:
            return self.permission_rules[rule_name](item, requester_role)
        return False


class PermissionDeniedError(Exception):
    """Raised when access is denied due to insufficient permissions."""

    def __init__(self, requester_role: str, required_permissions: List[str]):
        self.requester_role = requester_role
        self.required_permissions = required_permissions
        message = (
            f"Permission denied: Role '{requester_role}' does not have access. "
            f"Required permissions: {required_permissions}"
        )
        super().__init__(message)
