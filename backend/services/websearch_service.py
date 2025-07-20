"""
WebSearch Service module.
Handles web search functionality using MCP servers and fallback APIs.
Deprecated: Using tools from langchain_community instead for web search.
"""

import json
import logging
import os
import asyncio
import concurrent.futures
import re
from typing import Annotated, Dict, List, Optional
from operator import add

import requests
from bs4 import BeautifulSoup
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv
load_dotenv()

# class ChatState(TypedDict):
#     messages: Annotated[list[dict], add]
#     needs_search: bool
#     search_query: Optional[str]
#     search_results: Optional[str]


class WebSearchService:
    """Service for performing web searches using MCP servers and fallback APIs."""
    
    # MCP Configuration
    MCP_SERVER_CONFIG = {
        "brave_search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {
                "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")
            }
        }
    }
    
    def __init__(self, server_name: str = "web_search"):
        """Initialize the WebSearch service.
        
        Args:
            server_name: Name of the MCP server configuration to use
        """
        self.server_name = server_name
        self.server_config = self.MCP_SERVER_CONFIG.get(
            server_name, 
            self.MCP_SERVER_CONFIG["web_search"]
        )
        self.logger = logging.getLogger(f"{__name__}.WebSearchService")
        self.mcp_client = MCPWebSearchClient(server_name)
        
        # Initialize the LLM for search analysis
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform a web search using MCP server with fallback to direct API.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, and url
        """
        if not query.strip():
            self.logger.warning("Empty search query provided")
            return []
        
        self.logger.info(f"Performing web search for: '{query}'")
        
        try:
            # Try MCP search first
            results = await self.mcp_client.search(query, max_results)
            
            if results:
                self.logger.info(f"MCP search successful: {len(results)} results")
                return results
            else:
                self.logger.warning("MCP search returned no results, trying fallback")
                return await self._fallback_search(query, max_results)
                
        except Exception as e:
            self.logger.error(f"MCP search failed: {str(e)}")
            # Use fallback search
            return await self._fallback_search(query, max_results)
    
    def search_sync(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Synchronous wrapper for the async search method.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, and url
        """
        try:
            # Try to run in existing event loop if available
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, but this method is sync
                # Create a new thread to run the async operation
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.search(query, max_results))
                    return future.result(timeout=30)
            except RuntimeError:
                # No event loop running, create one
                return asyncio.run(self.search(query, max_results))
        except Exception as e:
            self.logger.error(f"Sync search failed: {str(e)}")
            # Return error as result
            return [{
                "title": "Search Error",
                "snippet": f"Search failed: {str(e)}. Please try again later.",
                "url": ""
            }]
    
    async def _fallback_search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Fallback search method using Brave Search API when MCP is not available.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        self.logger.warning("Using Brave Search API fallback method")
        
        try:
            brave_api_key = os.getenv("BRAVE_API_KEY")
            if not brave_api_key:
                self.logger.error("BRAVE_API_KEY not found in environment variables")
                return [{
                    "title": "Search Error",
                    "snippet": "Web search is currently unavailable. Please configure search API keys.",
                    "url": ""
                }]
            
            # Remove quotes from API key if present
            brave_api_key = brave_api_key.strip('"\'')
            
            # Brave Search API endpoint
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": brave_api_key
            }
            params = {
                "q": query,
                "count": min(max_results, 10),  # Brave API allows max 20
                "offset": 0,
                "mkt": "en-US",
                "safesearch": "moderate",
                "freshness": "pd",  # Past day for recent results
                "text_decorations": False,
                "search_lang": "en"
            }
            
            self.logger.debug(f"Making Brave Search API request for: '{query}'")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            search_results = []
            
            # Parse Brave Search results
            if "web" in data and "results" in data["web"]:
                for result in data["web"]["results"][:max_results]:
                    search_results.append({
                        "title": result.get("title", "No title"),
                        "snippet": result.get("description", "No description"),
                        "url": result.get("url", "")
                    })
                    search_results.append({
                        "title": result.get("title", "No title"),
                        "snippet": result.get("description", "No description"),
                        "url": result.get("url", "")
                    })
            
            self.logger.info(f"Found {len(search_results)} Brave search results")
            return search_results
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error in Brave Search API request: {str(e)}")
            return [{
                "title": "Search Error",
                "snippet": f"Web search failed: {str(e)}. Please try again later.",
                "url": ""
            }]
        except Exception as e:
            self.logger.error(f"Error in fallback search: {str(e)}")
            return [{
                "title": "Search Error", 
                "snippet": f"Search for '{query}' failed. Please try again later.",
                "url": ""
            }]
    
    def analyze_need_for_search(self, state: ChatState) -> dict:
        """Analyze if the current query needs web search using LLM."""
        try:
            # Extract content from the last message in state
            last_message = state["messages"][-1] if state["messages"] else {"content": ""}
            content = last_message.get("content", "")
            
            if not content.strip():
                return {"needs_search": False, "search_query": None}

            # Create a system prompt for search analysis
            analysis_prompt = SystemMessage(content="""You are a search decision assistant. Analyze the user's query and determine if it requires current/real-time information from the web.

Return your response in JSON format with these fields:
- "needs_search": boolean (true if web search is needed, false otherwise)
- "search_query": string (optimized search query if needed, null otherwise)
- "reasoning": string (brief explanation of your decision)

A query needs web search if it:
1. Asks for current events, news, or recent information
2. Requests real-time data (stock prices, weather, sports scores)
3. Asks about recent developments or updates
4. Needs facts that might have changed recently
5. Explicitly asks to search or look something up

A query does NOT need web search if it:
1. Asks for general knowledge that's unlikely to change
2. Requests explanations of concepts or principles
3. Asks for creative content (stories, poems, code examples)
4. Seeks advice or opinions
5. Is about historical information (unless asking about recent discoveries)

Examples:
- "What's the weather today?" → needs_search: true
- "Explain how photosynthesis works" → needs_search: false
- "Latest news about AI" → needs_search: true
- "Write a poem about cats" → needs_search: false""")

            user_query = HumanMessage(content=f"Analyze this query: '{content}'")

            # Call LLM for analysis
            response = self.llm.invoke([analysis_prompt, user_query])

            # Parse the LLM response
            try:
                response_text = response.content.strip()
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    analysis_result = json.loads(json_text)

                    needs_search = analysis_result.get("needs_search", False)
                    search_query = analysis_result.get("search_query", None) if needs_search else None
                    reasoning = analysis_result.get("reasoning", "No reasoning provided")

                    self.logger.debug(f"LLM search analysis: needs_search={needs_search}, query='{search_query}', reasoning='{reasoning}'")

                    # Update the state with the analysis results
                    return {
                        "needs_search": needs_search,
                        "search_query": search_query
                    }
                else:
                    response_lower = response_text.lower()
                    if "true" in response_lower or "yes" in response_lower:
                        self.logger.warning("LLM response not in JSON format, using fallback parsing")
                        return {
                            "needs_search": True,
                            "search_query": content
                        }
                    else:
                        return {
                            "needs_search": False,
                            "search_query": None
                        }

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
                self.logger.debug(f"LLM response was: {response.content}")
                return self.fallback_keyword_analysis(content)

        except Exception as e:
            self.logger.error(f"Error in analyze_need_for_search: {str(e)}", exc_info=True)
            return self.fallback_keyword_analysis(content)

    def fallback_keyword_analysis(self, content: str) -> dict:
        """Fallback keyword-based search analysis when LLM analysis fails."""
        self.logger.warning("Using fallback keyword-based search analysis")

        search_keywords = [
            "current", "latest", "recent", "new", "news", "today", "yesterday",
            "what happened", "what's happening", "stock price", "weather",
            "update", "breaking", "trending", "search", "find information",
            "look up", "real-time", "live", "now"
        ]

        needs_search = any(keyword in content.lower() for keyword in search_keywords)

        question_patterns = [
            r"\bwhat\s+is\s+the\s+current\b",
            r"\bwhat\s+are\s+the\s+latest\b",
            r"\bhow\s+much\s+is\b",
            r"\bwhen\s+did\b.*\bhappen\b",
            r"\bwho\s+is\s+the\s+current\b"
        ]

        for pattern in question_patterns:
            if re.search(pattern, content.lower()):
                needs_search = True
                break

        search_query = content if needs_search else None

        self.logger.debug(f"Fallback search analysis: needs_search={needs_search}, query='{search_query}'")

        return {
            "needs_search": needs_search,
            "search_query": search_query
        }

    def perform_web_search(self, state: ChatState) -> dict:
        """Perform web search using WebSearchService."""
        try:
            query = state.get("search_query", "")
            if not query:
                self.logger.warning("No search query provided")
                return {"search_results": "No search query provided"}

            self.logger.info(f"Performing web search for: '{query}'")

            # Use search_sync for search
            try:
                results = self.search_sync(query, max_results=5)
            except Exception as search_error:
                self.logger.error(f"Web search failed: {str(search_error)}")
                return {"search_results": f"Search temporarily unavailable: {str(search_error)}"}

            if not results:
                self.logger.warning(f"No search results found for query: '{query}'")
                return {"search_results": "No relevant search results found."}

            # Format search results
            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                snippet = result.get('snippet', result.get('body', 'No description'))
                url = result.get('url', result.get('href', ''))

                formatted_result = f"{i}. {title}\n{snippet}\nSource: {url}\n"
                formatted_results.append(formatted_result)

            search_summary = "\n".join(formatted_results)

            self.logger.info(f"Found {len(results)} search results")
            self.logger.debug(f"Search results length: {len(search_summary)} characters")

            return {"search_results": search_summary}

        except Exception as e:
            self.logger.error(f"Error in perform_web_search: {str(e)}", exc_info=True)
            return {"search_results": f"Search failed: {str(e)}"}

    def should_search(self, state: ChatState) -> str:
        """Determine the next node based on search analysis."""
        return "search" if state.get("needs_search", False) else "llm"

    def scrape_webpage(self, url: str, max_length: int = 2000) -> str:
        """Scrape content from a webpage."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()

            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            if len(text) > max_length:
                text = text[:max_length] + "..."

            return text

        except Exception as e:
            self.logger.warning(f"Failed to scrape {url}: {str(e)}")
            return f"Could not retrieve content from {url}"
    

class MCPWebSearchClient:
    """MCP client for web search functionality."""
    
    def __init__(self, server_name: str = "web_search"):
        """Initialize the MCP client.
        
        Args:
            server_name: Name of the MCP server configuration to use
        """
        self.server_name = server_name
        self.server_config = WebSearchService.MCP_SERVER_CONFIG.get(
            server_name, 
            WebSearchService.MCP_SERVER_CONFIG["web_search"]
        )
        self.logger = logging.getLogger(f"{__name__}.MCPWebSearchClient")
        
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform web search using MCP server.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, and url
        """
        try:
            self.logger.info(f"Performing MCP web search for: '{query}'")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.server_config["command"],
                args=self.server_config["args"],
                env=self.server_config.get("env", {})
            )
            
            # Connect to MCP server
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()
                    
                    # List available tools
                    tools = await session.list_tools()
                    self.logger.debug(f"Available MCP tools: {[tool.name for tool in tools.tools]}")
                    
                    # Find search tool
                    search_tool = None
                    for tool in tools.tools:
                        if "search" in tool.name.lower():
                            search_tool = tool
                            break
                    
                    if not search_tool:
                        raise ValueError("No search tool found in MCP server")
                    
                    # Perform search
                    result = await session.call_tool(
                        search_tool.name,
                        arguments={
                            "query": query,
                            "max_results": max_results
                        }
                    )
                    
                    # Parse results
                    search_results = []
                    if result.content:
                        for content in result.content:
                            if hasattr(content, 'text'):
                                # Parse the text response to extract structured results
                                text_content = content.text
                                # Assume the MCP server returns JSON or structured text
                                try:
                                    parsed_results = json.loads(text_content)
                                    if isinstance(parsed_results, list):
                                        search_results.extend(parsed_results)
                                    else:
                                        search_results.append(parsed_results)
                                except json.JSONDecodeError:
                                    # If not JSON, treat as plain text
                                    search_results.append({
                                        "title": "Search Result",
                                        "snippet": text_content,
                                        "url": ""
                                    })
                    
                    self.logger.info(f"Found {len(search_results)} MCP search results")
                    return search_results
                    
        except Exception as e:
            self.logger.error(f"Error in MCP web search: {str(e)}", exc_info=True)
            raise  # Re-raise to let the calling service handle fallback
