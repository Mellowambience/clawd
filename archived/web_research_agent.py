"""
Web Research Agent
Performs web scraping and data collection for research purposes
Integrates with Clawdbot Hub ecosystem for enhanced analysis
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import requests
import urllib.parse
from urllib.robotparser import RobotFileParser


class WebResearchAgent:
    """
    Agent that performs web scraping and data collection for research purposes
    Integrates with Clawdbot Hub ecosystem for enhanced analysis
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082"):
        self.hub_url = hub_url
        self.logger = self._setup_logger()
        self.session = None
        self.research_keywords = [
            'AI research', 'artificial intelligence', 'machine learning', 
            'consciousness studies', 'cognitive science', 'neuroscience',
            'ethics in AI', 'AI safety', 'technology ethics', 'digital consciousness',
            'philosophy of mind', 'computer science', 'deep learning', 'neural networks',
            'human-AI interaction', 'autonomous systems', 'algorithmic fairness'
        ]
        self.scraped_data_cache = {}

    def _setup_logger(self):
        """Setup agent logger"""
        logger = logging.getLogger("WebResearchAgent")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - WebResearchAgent - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def initialize(self):
        """Initialize the web research agent"""
        self.session = aiohttp.ClientSession()
        self.logger.info("Web Research Agent initialized and ready for data collection")
        
    async def close(self):
        """Close the agent session"""
        if self.session:
            await self.session.close()

    async def check_robots_txt(self, url: str) -> bool:
        """Check robots.txt to ensure scraping is allowed"""
        try:
            parsed_url = urllib.parse.urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            async with self.session.get(robots_url, timeout=10) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    rp = RobotFileParser()
                    rp.parse(robots_content.splitlines())
                    return rp.can_fetch('*', url)
                else:
                    # If no robots.txt, assume allowed
                    return True
        except:
            # If robots.txt check fails, assume allowed
            return True

    async def scrape_webpage(self, url: str) -> Dict[str, Any]:
        """Scrape a webpage for content"""
        try:
            # Check robots.txt first
            if not await self.check_robots_txt(url):
                self.logger.warning(f"Scraping not allowed by robots.txt for {url}")
                return {"error": "Scraping not allowed by robots.txt"}
            
            # Use requests for synchronous scraping (more reliable for parsing)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract main content
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Look for main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.body
            if main_content:
                # Extract paragraphs
                paragraphs = main_content.find_all('p')
                content_text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                
                # Limit content length
                content_text = content_text[:2000]  # Limit to 2000 chars
            else:
                content_text = ""
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc:
                meta_desc = soup.find('meta', attrs={'property': 'og:description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            # Extract relevant links
            links = []
            for link in soup.find_all('a', href=True)[:10]:  # Limit to 10 links
                href = link['href']
                if href.startswith(('http://', 'https://')):
                    links.append(href)
                elif href.startswith('/'):
                    links.append(urllib.parse.urljoin(url, href))
            
            scraped_data = {
                'url': url,
                'title': title_text,
                'content': content_text,
                'description': description,
                'links': links,
                'scraped_at': datetime.now().isoformat(),
                'source_domain': urllib.parse.urlparse(url).netloc
            }
            
            self.scraped_data_cache[url] = scraped_data
            self.logger.info(f"Successfully scraped webpage: {title_text[:50]}...")
            
            return scraped_data
            
        except Exception as e:
            self.logger.error(f"Error scraping webpage {url}: {e}")
            return {"error": str(e)}

    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web for relevant information"""
        # Note: This is a simplified implementation
        # In a production system, you'd use a proper search API like Google Custom Search
        # For now, we'll simulate by searching for common research sites
        
        search_urls = [
            f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(query)}",
            f"https://scholar.google.com/scholar?q={urllib.parse.quote(query)}",
            f"https://arxiv.org/search/?query={urllib.parse.quote(query)}"
        ]
        
        results = []
        for url in search_urls[:num_results]:
            try:
                # This is a simplified approach - in practice you'd use a proper search API
                # For now, we'll just return the URLs as potential sources
                results.append({
                    'url': url,
                    'title': f"Search results for: {query}",
                    'snippet': f"Potential research sources for query: {query}",
                    'searched_at': datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error in web search: {e}")
        
        return results

    async def analyze_scraped_data(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scraped data for research insights"""
        if 'error' in scraped_data:
            return {'analysis': 'Error in scraped data', 'quality_score': 0.0}
        
        content = scraped_data.get('content', '')
        title = scraped_data.get('title', '')
        combined_text = f"{title} {content}".lower()
        
        # Calculate research relevance
        research_score = 0.0
        for keyword in self.research_keywords:
            if keyword.lower() in combined_text:
                research_score += 0.1
        
        # Content quality indicators
        content_length = len(content)
        quality_indicators = ['study', 'research', 'analysis', 'data', 'findings', 'results', 'methodology']
        quality_score = sum(1 for indicator in quality_indicators if indicator in content.lower()) * 0.1
        
        # Combine scores
        total_score = min(research_score + quality_score, 1.0)
        
        analysis = {
            'research_relevance': research_score,
            'content_quality': quality_score,
            'overall_score': total_score,
            'key_topics': self._extract_key_topics(combined_text),
            'summary': self._generate_summary(content),
            'research_value': self._assess_research_value(scraped_data)
        }
        
        return analysis

    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from text"""
        # Simple keyword extraction based on our research keywords
        topics = []
        for keyword in self.research_keywords:
            if keyword.lower() in text:
                topics.append(keyword)
        return list(set(topics))[:5]  # Return top 5 unique topics

    def _generate_summary(self, content: str) -> str:
        """Generate a brief summary of the content"""
        if len(content) < 200:
            return content
        
        # Simple summarization by taking first 200 characters and finding sentence boundary
        snippet = content[:200]
        last_period = snippet.rfind('.')
        if last_period > 100:  # If period found in reasonable place
            return snippet[:last_period + 1]
        else:
            return snippet + "..."

    def _assess_research_value(self, scraped_data: Dict[str, Any]) -> str:
        """Assess the research value of the content"""
        content = scraped_data.get('content', '')
        title = scraped_data.get('title', '')
        
        # Look for research indicators
        if any(indicator in title.lower() for indicator in ['study', 'research', 'paper', 'analysis']):
            return "high"
        elif any(indicator in content.lower() for indicator in ['data', 'findings', 'results', 'methodology', 'experiment']):
            return "medium"
        else:
            return "low"

    async def relay_research_to_hub(self, scraped_data: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[Dict]:
        """Relay research findings to Clawdbot Hub"""
        if 'error' in scraped_data:
            return None
            
        content = f"""
Web Research Findings
====================

🌐 **Source**: [{scraped_data.get('title', 'Untitled')}]({scraped_data.get('url')})

📋 **Summary**: {analysis.get('summary', 'No summary available')}

🔍 **Key Topics**: {', '.join(analysis.get('key_topics', []))}

📊 **Research Analysis**:
- Research Relevance: {analysis.get('research_relevance', 0):.2f}
- Content Quality: {analysis.get('content_quality', 0):.2f}
- Overall Score: {analysis.get('overall_score', 0):.2f}
- Research Value: {analysis.get('research_value', 'unknown')}

🔗 **Related Links**: {len(scraped_data.get('links', []))} additional resources found

#WebResearch #DataCollection #ResearchUpdate #AIStudies
        """.strip()
        
        try:
            post_data = {
                'author': 'Web-Research-Agent',
                'content': content,
                'title': f'Web Research: {scraped_data.get("title", "Untitled")}',
                'timestamp': datetime.now().isoformat(),
                'isAgentPost': True,
                'isResearchPost': True,
                'researchSource': 'WebScraping',
                'quality_score': analysis.get('overall_score', 0.0),
                'research_based': True,
                'truth_seeking': True,
                'value_focused': True,
                'contentType': 'research_summary'
            }
            
            async with self.session.post(f"{self.hub_url}/api/posts", json=post_data) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    self.logger.info("Successfully relayed web research to hub")
                    return result
                else:
                    self.logger.error(f"Failed to relay research to hub: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error relaying research to hub: {e}")
            return None

    async def conduct_research_on_topic(self, topic: str) -> bool:
        """Conduct research on a specific topic"""
        self.logger.info(f"Starting web research on topic: {topic}")
        
        # Search for relevant sources
        search_results = await self.search_web(topic, num_results=3)
        
        for result in search_results:
            url = result.get('url')
            if url:
                # Scrape the page
                scraped_data = await self.scrape_webpage(url)
                
                if 'error' not in scraped_data:
                    # Analyze the data
                    analysis = await self.analyze_scraped_data(scraped_data)
                    
                    # Relay to hub
                    await self.relay_research_to_hub(scraped_data, analysis)
        
        self.logger.info(f"Completed web research on topic: {topic}")
        return True

    async def continuous_monitoring(self, topics: List[str] = None, interval_hours: int = 6):
        """Continuously monitor web for research topics"""
        if topics is None:
            topics = ['AI research', 'consciousness studies', 'technology ethics']
            
        self.logger.info(f"Starting continuous web research on topics: {topics}")
        
        while True:
            for topic in topics:
                await self.conduct_research_on_topic(topic)
                
            # Wait before next research cycle
            await asyncio.sleep(interval_hours * 3600)


# Example usage
async def main():
    agent = WebResearchAgent()
    await agent.initialize()
    
    print("Web Research Agent initialized")
    print("This agent will scrape web pages and collect research data")
    print("then relay findings to the Clawdbot Hub for further analysis.")
    
    # Example: Scrape a specific page
    # result = await agent.scrape_webpage("https://en.wikipedia.org/wiki/Artificial_intelligence")
    # print(result)
    
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())