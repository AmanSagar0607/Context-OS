"""
Tests for LLM-based Planner.

Tests both the LLM planning and keyword fallback.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from the planner module to avoid __init__.py imports
from agents.planner import (
    create_plan, 
    create_plan_async, 
    QueryType, 
    TaskAction,
    _classify_query,
    _plan_steps,
    _parse_llm_plan,
    Plan,
    PlanStep,
)


class TestKeywordPlanner:
    """Tests for keyword-based planning (fallback)."""
    
    def test_memory_query(self):
        plan = create_plan("remember my name is John")
        assert plan.query_type == QueryType.MEMORY
        assert any(s.action == TaskAction.REMEMBER for s in plan.steps)
    
    def test_research_query(self):
        plan = create_plan("search for latest AI news")
        assert plan.query_type == QueryType.RESEARCH
        assert any(s.action == TaskAction.SEARCH for s in plan.steps)
    
    def test_document_query(self):
        plan = create_plan("what's in this PDF?")
        assert plan.query_type == QueryType.DOCUMENT
        assert any(s.action == TaskAction.RETRIEVE for s in plan.steps)
    
    def test_knowledge_query(self):
        plan = create_plan("extract all company names from this text")
        assert plan.query_type == QueryType.KNOWLEDGE
        assert any(s.action == TaskAction.EXTRACT for s in plan.steps)
    
    def test_workflow_query(self):
        plan = create_plan("monitor this website daily")
        assert plan.query_type == QueryType.WORKFLOW
        assert any(s.action == TaskAction.MONITOR for s in plan.steps)
    
    def test_hybrid_query(self):
        plan = create_plan("search for latest AI news and remember my preference")
        assert plan.query_type == QueryType.HYBRID
        assert len(plan.steps) >= 2
    
    def test_general_query(self):
        plan = create_plan("hello")
        assert plan.query_type == QueryType.GENERAL
    
    def test_url_detection(self):
        plan = create_plan("scrape https://example.com")
        assert plan.query_type == QueryType.RESEARCH
        assert any(s.action == TaskAction.SCRAPE for s in plan.steps)


class TestLLMPlanner:
    """Tests for LLM-based planning."""
    
    @pytest.mark.asyncio
    async def test_llm_plan_success(self):
        mock_response = {
            "query_type": "research",
            "confidence": 0.9,
            "reasoning": "User wants to search for information",
            "refined_query": "latest AI news",
            "steps": [
                {
                    "action": "search",
                    "description": "Search for latest AI news",
                    "agent": "research",
                    "priority": 1,
                    "params": {},
                    "depends_on": [],
                }
            ]
        }
        
        mock_settings = MagicMock()
        mock_settings.openrouter_api_key = "test-key"
        mock_settings.openrouter_model = "test-model"
        
        with patch("agents.planner._call_llm_for_planning", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            
            with patch("app.config.get_settings", return_value=mock_settings):
                plan = await create_plan_async("search for latest AI news")
                
                assert plan.query_type == QueryType.RESEARCH
                assert len(plan.steps) == 1
                assert plan.steps[0].action == TaskAction.SEARCH
                assert plan.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_llm_fallback_to_keywords(self):
        mock_settings = MagicMock()
        mock_settings.openrouter_api_key = "test-key"
        mock_settings.openrouter_model = "test-model"
        
        with patch("agents.planner._call_llm_for_planning", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = None  # LLM fails
            
            with patch("app.config.get_settings", return_value=mock_settings):
                plan = await create_plan_async("remember my name")
                
                # Should fallback to keyword planning
                assert plan.query_type == QueryType.MEMORY
                assert any(s.action == TaskAction.REMEMBER for s in plan.steps)
    
    @pytest.mark.asyncio
    async def test_llm_no_api_key_fallback(self):
        mock_settings = MagicMock()
        mock_settings.openrouter_api_key = ""
        
        with patch("app.config.get_settings", return_value=mock_settings):
            plan = await create_plan_async("search for something")
            
            # Should use keyword planning
            assert plan.query_type == QueryType.RESEARCH


class TestParseLLMPlan:
    """Tests for parsing LLM responses."""
    
    def test_parse_valid_plan(self):
        llm_response = {
            "query_type": "memory",
            "confidence": 0.85,
            "reasoning": "User wants to store information",
            "refined_query": "remember my preference",
            "steps": [
                {
                    "action": "remember",
                    "description": "Store user preference",
                    "agent": "memory",
                    "priority": 1,
                    "params": {},
                    "depends_on": [],
                },
                {
                    "action": "answer",
                    "description": "Confirm memory stored",
                    "agent": "memory",
                    "priority": 2,
                    "params": {},
                    "depends_on": [0],
                }
            ]
        }
        
        plan = _parse_llm_plan(llm_response, "remember my preference")
        
        assert plan is not None
        assert plan.query_type == QueryType.MEMORY
        assert len(plan.steps) == 2
        assert plan.steps[0].depends_on == []
        assert plan.steps[1].depends_on == [0]
    
    def test_parse_invalid_json(self):
        plan = _parse_llm_plan({"invalid": "data"}, "test")
        assert plan is None
    
    def test_parse_empty_steps(self):
        llm_response = {
            "query_type": "general",
            "confidence": 0.5,
            "reasoning": "No steps needed",
            "steps": []
        }
        
        plan = _parse_llm_plan(llm_response, "test")
        assert plan is None


class TestClassifyQuery:
    """Tests for query classification."""
    
    def test_document_keywords(self):
        query_type, confidence, reasoning = _classify_query("upload this PDF")
        assert query_type == QueryType.DOCUMENT
        assert confidence > 0
    
    def test_memory_keywords(self):
        query_type, confidence, reasoning = _classify_query("remember my name")
        assert query_type == QueryType.MEMORY
        assert confidence > 0
    
    def test_research_keywords(self):
        query_type, confidence, reasoning = _classify_query("search for latest news")
        assert query_type == QueryType.RESEARCH
        assert confidence > 0
