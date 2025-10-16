"""
PostgreSQL storage for agents, roles, and audit logs.

Handles security-critical and relational data.
"""

import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import json


class PostgreSQLStore:
    """
    PostgreSQL storage for agents, roles, and audit logs.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "agentmesh",
        user: str = "postgres",
        password: str = "postgres"
    ):
        """
        Initialize PostgreSQL connection.

        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: Database name
            user: Database user
            password: Database password
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.conn = None
        self._connect()
        self._initialize_schema()

    def _connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = False
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")

    @contextmanager
    def _cursor(self):
        """Context manager for database cursor."""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def _initialize_schema(self):
        """Create tables if they don't exist."""
        schema_sql = """
        -- Roles table
        CREATE TABLE IF NOT EXISTS roles (
            role_name VARCHAR(100) PRIMARY KEY,
            description TEXT,
            can_access_roles TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
            can_publish BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Agents table
        CREATE TABLE IF NOT EXISTS agents (
            id VARCHAR(255) PRIMARY KEY,
            framework VARCHAR(100) NOT NULL,
            role VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            last_active TIMESTAMP,
            status VARCHAR(50) DEFAULT 'active',
            metadata JSONB DEFAULT '{}'::JSONB,
            CONSTRAINT fk_agent_role FOREIGN KEY (role)
                REFERENCES roles(role_name) ON DELETE RESTRICT
        );

        -- Audit logs table
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            agent_id VARCHAR(255),
            action VARCHAR(100) NOT NULL,
            resource_type VARCHAR(50),
            resource_id VARCHAR(255),
            details JSONB,
            timestamp TIMESTAMP DEFAULT NOW()
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_agents_role ON agents(role);
        CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
        CREATE INDEX IF NOT EXISTS idx_agents_last_active ON agents(last_active);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_agent ON audit_logs(agent_id);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
        """

        with self._cursor() as cur:
            cur.execute(schema_sql)

        # Seed default roles if table is empty
        self._seed_default_roles()

    def _seed_default_roles(self):
        """Seed default roles if none exist."""
        with self._cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM roles")
            count = cur.fetchone()['count']

            if count == 0:
                default_roles = [
                    ('sales', 'Sales department agents', ['sales']),
                    ('marketing', 'Marketing department agents', ['marketing', 'sales']),
                    ('inventory', 'Inventory management agents', ['inventory', 'sales', 'marketing']),
                    ('finance', 'Finance department agents', ['finance']),
                    ('engineering', 'Engineering department agents', ['engineering']),
                    ('executive', 'Executive-level agents',
                     ['sales', 'marketing', 'inventory', 'finance', 'engineering', 'executive']),
                    ('admin', 'System administrators',
                     ['sales', 'marketing', 'inventory', 'finance', 'engineering', 'executive', 'admin'])
                ]

                for role_name, description, can_access in default_roles:
                    cur.execute("""
                        INSERT INTO roles (role_name, description, can_access_roles)
                        VALUES (%s, %s, %s)
                    """, (role_name, description, can_access))

    # ===== Agent Operations =====

    def register_agent(
        self,
        agent_id: str,
        framework: str,
        role: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a new agent.

        Args:
            agent_id: Unique agent identifier
            framework: Framework name
            role: Agent role
            metadata: Additional metadata

        Returns:
            True if registered, False if already exists
        """
        with self._cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO agents (id, framework, role, metadata, last_active)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (agent_id, framework, role, json.dumps(metadata or {})))

                # Log registration
                self._log_action_internal(cur, agent_id, 'agent_registered',
                                         'agent', agent_id,
                                         {'framework': framework, 'role': role})
                return True
            except psycopg2.IntegrityError:
                # Agent already exists
                return False

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID."""
        with self._cursor() as cur:
            cur.execute("""
                SELECT id, framework, role, created_at, last_active, status, metadata
                FROM agents
                WHERE id = %s
            """, (agent_id,))
            result = cur.fetchone()
            return dict(result) if result else None

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all agents."""
        with self._cursor() as cur:
            cur.execute("""
                SELECT id, framework, role, created_at, last_active, status, metadata
                FROM agents
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in cur.fetchall()]

    def get_agents_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Get all agents with a specific role."""
        with self._cursor() as cur:
            cur.execute("""
                SELECT id, framework, role, created_at, last_active, status, metadata
                FROM agents
                WHERE role = %s
                ORDER BY created_at DESC
            """, (role,))
            return [dict(row) for row in cur.fetchall()]

    def update_agent_last_active(self, agent_id: str):
        """Update agent's last active timestamp."""
        with self._cursor() as cur:
            cur.execute("""
                UPDATE agents
                SET last_active = NOW()
                WHERE id = %s
            """, (agent_id,))

    def agent_exists(self, agent_id: str) -> bool:
        """Check if agent exists."""
        with self._cursor() as cur:
            cur.execute("""
                SELECT EXISTS(SELECT 1 FROM agents WHERE id = %s)
            """, (agent_id,))
            return cur.fetchone()['exists']

    # ===== Role Operations =====

    def get_role(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Get role by name."""
        with self._cursor() as cur:
            cur.execute("""
                SELECT role_name, description, can_access_roles, can_publish, created_at
                FROM roles
                WHERE role_name = %s
            """, (role_name,))
            result = cur.fetchone()
            return dict(result) if result else None

    def get_all_roles(self) -> List[Dict[str, Any]]:
        """Get all roles."""
        with self._cursor() as cur:
            cur.execute("""
                SELECT role_name, description, can_access_roles, can_publish, created_at
                FROM roles
                ORDER BY role_name
            """)
            return [dict(row) for row in cur.fetchall()]

    def get_agent_permissions(self, agent_id: str) -> List[str]:
        """
        Get what roles an agent can access based on their role.

        Args:
            agent_id: Agent ID

        Returns:
            List of accessible role names
        """
        with self._cursor() as cur:
            cur.execute("""
                SELECT r.can_access_roles
                FROM agents a
                JOIN roles r ON r.role_name = a.role
                WHERE a.id = %s
            """, (agent_id,))
            result = cur.fetchone()
            return result['can_access_roles'] if result else []

    def can_access(self, agent_id: str, required_permissions: List[str]) -> bool:
        """
        Check if agent can access resources with given permissions.

        Args:
            agent_id: Agent ID
            required_permissions: Required permissions (roles)

        Returns:
            True if agent can access
        """
        accessible_roles = self.get_agent_permissions(agent_id)

        # Check if any required permission is in accessible roles
        for perm in required_permissions:
            if perm in accessible_roles:
                return True

        return False

    # ===== Audit Log Operations =====

    def log_action(
        self,
        agent_id: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log an action to audit trail.

        Args:
            agent_id: Agent performing action
            action: Action name
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Additional details
        """
        with self._cursor() as cur:
            self._log_action_internal(cur, agent_id, action,
                                     resource_type, resource_id, details)

    def _log_action_internal(
        self,
        cursor,
        agent_id: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Internal method to log action (for use within transactions)."""
        cursor.execute("""
            INSERT INTO audit_logs (agent_id, action, resource_type, resource_id, details)
            VALUES (%s, %s, %s, %s, %s)
        """, (agent_id, action, resource_type, resource_id, json.dumps(details or {})))

    def get_audit_logs(
        self,
        agent_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs with optional filters.

        Args:
            agent_id: Filter by agent
            action: Filter by action
            limit: Maximum number of logs

        Returns:
            List of audit log entries
        """
        with self._cursor() as cur:
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []

            if agent_id:
                query += " AND agent_id = %s"
                params.append(agent_id)

            if action:
                query += " AND action = %s"
                params.append(action)

            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)

            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    # ===== Connection Management =====

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
