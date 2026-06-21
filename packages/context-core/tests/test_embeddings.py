"""
Tests for embedding service — Mock-based tests without model loading.
"""

import sys
from pathlib import Path
from importlib import import_module

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import MagicMock, patch

# Import the real module directly from the file path to avoid
# contamination from test_consolidation.py's sys.modules patches
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "embeddings.service",
    str(Path(__file__).parent.parent / "embeddings" / "service.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
EmbeddingService = _mod.EmbeddingService
SentenceTransformerProvider = _mod.SentenceTransformerProvider


class TestEmbeddingService:
    """Test embedding service with mocks."""

    def test_service_initialization(self):
        """EmbeddingService initializes with correct provider."""
        service = EmbeddingService(
            provider="sentence-transformers",
            model_name="all-MiniLM-L6-v2",
            dimension=384,
        )
        assert service.provider_name == "sentence-transformers"
        assert service.dimension == 384

    def test_openai_provider_initialization(self):
        """EmbeddingService can use OpenAI provider."""
        service = EmbeddingService(
            provider="openai",
            model_name="text-embedding-3-small",
            api_key="test-key",
            dimension=1536,
        )
        assert service.provider_name == "openai"
        assert service.dimension == 1536

    @patch.object(SentenceTransformerProvider, "embed_query", return_value=[0.1, 0.2, 0.3])
    def test_embed_query_calls_provider(self, mock_embed):
        """embed_query delegates to provider."""
        service = EmbeddingService(provider="sentence-transformers")
        result = service.embed_query("test query")

        mock_embed.assert_called_once_with("test query")
        assert result == [0.1, 0.2, 0.3]

    @patch.object(SentenceTransformerProvider, "embed_texts")
    def test_embed_texts_calls_provider(self, mock_embed):
        """embed_texts delegates to provider."""
        mock_embed.return_value = {
            "model": "all-MiniLM-L6-v2",
            "dimension": 384,
            "count": 2,
            "vectors": [[0.1, 0.2], [0.3, 0.4]],
            "duration_ms": 10.5,
        }

        service = EmbeddingService(provider="sentence-transformers")
        result = service.embed_texts(["text1", "text2"])

        mock_embed.assert_called_once_with(["text1", "text2"])
        assert result["count"] == 2
        assert len(result["vectors"]) == 2

    def test_from_settings_factory(self):
        """from_settings creates service from Settings object."""
        mock_settings = MagicMock()
        mock_settings.embedding_provider = "sentence-transformers"
        mock_settings.embedding_model = "all-MiniLM-L6-v2"
        mock_settings.embedding_dimension = 384

        service = EmbeddingService.from_settings(mock_settings)
        assert service.provider_name == "sentence-transformers"
        assert service.dimension == 384