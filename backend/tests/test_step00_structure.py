"""STEP 00 Verification Tests: Monorepo Structure, Architecture Rules, and Config Integrity."""

import importlib
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class TestStep00ArchitectureStructure(unittest.TestCase):
    """Verifies that all STEP 00 directories, packages, and governance documents exist."""

    def test_top_level_directories_exist(self) -> None:
        required_dirs = [
            "frontend",
            "backend",
            "collectors",
            "skills",
            "docs",
            "infra",
        ]
        for dir_name in required_dirs:
            target = REPO_ROOT / dir_name
            self.assertTrue(target.is_dir(), f"Missing top-level directory: {dir_name}")

    def test_backend_mandatory_packages_exist_and_import(self) -> None:
        required_packages = [
            "api",
            "core",
            "schemas",
            "services",
            "repositories",
            "orchestration",
            "agents",
            "rag",
            "rules",
            "validators",
            "adapters",
            "collection",
            "tools",
            "mcp",
            "history",
            "workers",
        ]
        app_root = BACKEND_ROOT / "app"
        self.assertTrue((app_root / "__init__.py").is_file(), "Missing backend/app/__init__.py")

        for pkg in required_packages:
            pkg_dir = app_root / pkg
            init_file = pkg_dir / "__init__.py"
            self.assertTrue(pkg_dir.is_dir(), f"Missing backend package directory: {pkg}")
            self.assertTrue(init_file.is_file(), f"Missing __init__.py in backend package: {pkg}")
            mod = importlib.import_module(f"app.{pkg}")
            self.assertIsNotNone(mod.__doc__, f"Package app.{pkg} is missing module docstring")

        # Verify MySQL MVP adapter package exists and imports cleanly
        mysql_adapter_init = app_root / "adapters" / "mysql" / "__init__.py"
        self.assertTrue(mysql_adapter_init.is_file(), "Missing backend/app/adapters/mysql/__init__.py")
        mysql_mod = importlib.import_module("app.adapters.mysql")
        self.assertIsNotNone(mysql_mod.__doc__)

    def test_mandatory_documentation_and_config_files_exist(self) -> None:
        required_files = [
            "AGENTS.md",
            "README.md",
            ".env.example",
            ".gitignore",
            "docker-compose.yml",
            "docs/ARCHITECTURE.md",
            "docs/REQUIREMENTS.md",
            "docs/DEVELOPMENT_PLAN.md",
            "infra/postgres/init/01-init-pgvector.sql",
            "infra/docker/backend.Dockerfile",
            "infra/docker/frontend.Dockerfile",
        ]
        for rel_path in required_files:
            file_path = REPO_ROOT / rel_path
            self.assertTrue(file_path.is_file(), f"Missing required file: {rel_path}")
            self.assertGreater(file_path.stat().st_size, 0, f"File is empty: {rel_path}")

    def test_agents_md_contains_core_architecture_and_security_rules(self) -> None:
        agents_md = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        expected_keywords = [
            "MySQL 8.0",
            "8.4",
            "SQLGlot",
            "Evidence Validator",
            "InventoryModel",
            "Read-Only",
            "dev.mysql.com",
            "adapters",
        ]
        for keyword in expected_keywords:
            self.assertIn(keyword, agents_md, f"AGENTS.md missing required rule keyword: {keyword}")

    def test_env_example_and_docker_compose_integrity(self) -> None:
        env_example = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
        for key in [
            "DATABASE_URL=",
            "SECRET_KEY=",
            "DB_CREDENTIAL_ENCRYPTION_KEY=",
            "TARGET_DB_READ_ONLY=true",
            "ALLOWED_DOC_DOMAINS=dev.mysql.com,downloads.mysql.com",
        ]:
            self.assertIn(key, env_example, f".env.example missing configuration: {key}")

        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        for token in [
            "pgvector/pgvector:pg16",
            "./infra/postgres/init:/docker-entrypoint-initdb.d:ro",
            "pg_isready",
            "postgres_data:",
            "upgrade-agent-net:",
        ]:
            self.assertIn(token, compose_text, f"docker-compose.yml missing token: {token}")

        pgvector_sql = (REPO_ROOT / "infra/postgres/init/01-init-pgvector.sql").read_text(encoding="utf-8")
        self.assertIn("CREATE EXTENSION IF NOT EXISTS vector;", pgvector_sql)

    def test_git_repository_initialized(self) -> None:
        git_dir = REPO_ROOT / ".git"
        head_file = git_dir / "HEAD"
        self.assertTrue(git_dir.is_dir(), "Missing .git directory")
        self.assertTrue(head_file.is_file(), "Missing .git/HEAD file")
        self.assertIn("refs/heads/main", head_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
