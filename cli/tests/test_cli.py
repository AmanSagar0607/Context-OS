"""
Context OS — CLI Tests

Tests for CLI commands.
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from context_cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Context OS" in result.output

    def test_memory_help(self, runner):
        result = runner.invoke(cli, ["memory", "--help"])
        assert result.exit_code == 0
        assert "Memory operations" in result.output

    def test_search_help(self, runner):
        result = runner.invoke(cli, ["search", "--help"])
        assert result.exit_code == 0
        assert "Search operations" in result.output

    def test_crawl_help(self, runner):
        result = runner.invoke(cli, ["crawl", "--help"])
        assert result.exit_code == 0
        assert "Web crawl operations" in result.output

    def test_knowledge_help(self, runner):
        result = runner.invoke(cli, ["knowledge", "--help"])
        assert result.exit_code == 0
        assert "Knowledge graph" in result.output

    @patch("context_cli.main._get_client")
    def test_health(self, mock_get_client, runner):
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok",
            "version": "0.1.0",
            "services": {"postgres": "connected"},
        }
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = runner.invoke(cli, ["health"])
        assert result.exit_code == 0
        assert "ok" in result.output.lower() or "health" in result.output.lower()

    @patch("context_cli.main._get_client")
    def test_memory_add_help(self, mock_get_client, runner):
        result = runner.invoke(cli, ["memory", "add", "--help"])
        assert result.exit_code == 0
        assert "Memory content" in result.output

    @patch("context_cli.main._get_client")
    def test_memory_search_help(self, mock_get_client, runner):
        result = runner.invoke(cli, ["memory", "search", "--help"])
        assert result.exit_code == 0
        assert "query" in result.output.lower()