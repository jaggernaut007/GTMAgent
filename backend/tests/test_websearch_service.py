import pytest
from services.websearch_service import WebSearchService

@pytest.fixture
def web_search_service():
    return WebSearchService()

def test_analyze_need_for_search(web_search_service):
    query = "What's the weather today?"
    result = web_search_service.analyze_need_for_search(query)
    assert result["needs_search"] is True
    assert result["search_query"] == query

def test_fallback_keyword_analysis(web_search_service):
    query = "Latest news about AI"
    result = web_search_service.fallback_keyword_analysis(query)
    assert result["needs_search"] is True
    assert result["search_query"] == query

def test_should_search(web_search_service):
    state = {
        "needs_search": True,
        "search_query": "What's the weather today?"
    }
    next_node = web_search_service.should_search(state)
    assert next_node == "search"

def test_scrape_webpage(web_search_service):
    url = "https://example.com"
    content = web_search_service.scrape_webpage(url)
    assert isinstance(content, str)
    assert len(content) > 0
