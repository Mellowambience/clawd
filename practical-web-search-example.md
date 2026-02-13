# Practical Web Search and Scraping Examples

## Overview
This document provides practical examples of how to use Moltbot's web search and scraping tools effectively.

## Tool Integration Examples

### 1. Basic Web Search
```python
# Search for information using web_search tool
search_results = web_search(query="latest developments in artificial intelligence", count=5)

# Process the results
for result in search_results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Snippet: {result['snippet']}")
    print("---")
```

### 2. Content Extraction from Search Results
```python
# First search for relevant URLs
search_results = web_search(query="impact of AI on healthcare", count=3)

# Then extract content from the top results
extracted_contents = []
for result in search_results:
    try:
        content = web_fetch(url=result['url'])
        extracted_contents.append({
            'url': result['url'],
            'title': result['title'],
            'content': content
        })
    except Exception as e:
        print(f"Failed to fetch {result['url']}: {str(e)}")
```

### 3. Advanced Browser Automation
```python
# For complex sites that require JavaScript rendering
browser.start(profile="chrome")  # Use existing Chrome with extensions if available

# Navigate to a page
browser.open(url="https://news.example-site.com")

# Take a snapshot to see available elements
snapshot = browser.snapshot()

# Interact with elements using the snapshot references
browser.act(request={
    "kind": "click",
    "ref": "article-link-123"  # Use reference from snapshot
})

# Extract specific content after interaction
content_snapshot = browser.snapshot()
# Process the content_snapshot to extract needed information

browser.stop()
```

## Real-World Research Workflow

### Research Task: "Analyze current trends in renewable energy technology"

#### Step 1: Initial Search
```python
# Search for broad information
trends_results = web_search(
    query="renewable energy technology trends 2026",
    count=5,
    freshness="py"  # Past year for current information
)
```

#### Step 2: Content Extraction
```python
# Extract content from promising sources
trend_articles = []
for result in trends_results[:3]:  # Top 3 results
    try:
        content = web_fetch(url=result['url'], maxChars=5000)  # Limit content size
        trend_articles.append({
            'title': result['title'],
            'url': result['url'],
            'content': content,
            'source_domain': result['url'].split('/')[2]
        })
    except Exception as e:
        continue  # Skip if unable to fetch
```

#### Step 3: Deep Analysis with Browser
```python
# For specific sites with dynamic content
for article in trend_articles:
    if 'reuters.com' in article['url']:  # Example: specific handling for Reuters
        browser.start(profile="chrome")
        try:
            browser.open(url=article['url'])
            # Wait for dynamic content to load
            time.sleep(2)
            detailed_snapshot = browser.snapshot()
            # Extract specific elements like charts, specific paragraphs, etc.
        finally:
            browser.stop()
```

## Best Practices

### 1. Search Optimization
- Use specific, targeted keywords
- Include relevant terms like "2026", "recent", "latest" for current information
- Use site-specific searches when needed: `"site:edu research paper"`
- Combine terms with AND/OR logic when needed

### 2. Content Extraction
- Always implement error handling around web_fetch calls
- Limit content size to avoid overwhelming the context window
- Extract only the most relevant sections when possible
- Verify content quality before processing

### 3. Browser Automation
- Only use browser automation when web_fetch is insufficient
- Be respectful of website resources (add delays when needed)
- Always stop browsers after use to free resources
- Use Chrome profile when you need extensions or logged-in states

## Data Processing Pipeline

### 1. Collection Phase
```python
# Collect from multiple sources
all_data = []

# Search engines
search_data = web_search(query="your_query", count=5)

# Direct URL content
for url in known_urls:
    content = web_fetch(url=url)
    all_data.append({'source': 'web_fetch', 'data': content})

# Browser automation for complex sites
for dynamic_url in dynamic_urls:
    browser.start()
    # ... browser operations ...
    browser.stop()
```

### 2. Cleaning Phase
```python
# Remove duplicates
unique_sources = []
cleaned_data = []

for item in all_data:
    if item['url'] not in unique_sources:
        unique_sources.append(item['url'])
        cleaned_data.append(item)
```

### 3. Analysis Phase
```python
# Feed to AI for analysis
analysis_prompt = f"""
Analyze the following articles about renewable energy trends:

{"---".join([f"Title: {item['title']}\nContent: {item['content'][:1000]}" for item in cleaned_data])}

Provide a summary of key trends, technologies, and predictions.
"""

# Use AI to analyze the collected data
analysis_result = ai.analyze(analysis_prompt)
```

## Error Handling and Robustness

### 1. Retry Logic
```python
def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            return web_fetch(url=url)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 2. Fallback Strategies
```python
def get_content_flexible(url):
    # Try web_fetch first
    try:
        return web_fetch(url=url, extractMode="markdown")
    except:
        # Fallback to browser automation
        try:
            browser.start()
            browser.open(url=url)
            snapshot = browser.snapshot()
            # Extract content from snapshot
            return snapshot.content  # Simplified
        finally:
            browser.stop()
```

## Integration with Other Moltbot Systems

### Memory Integration
```python
# Store research findings in memory
for article in research_results:
    memory_add(
        content=f"Research: {article['title']}\nURL: {article['url']}\nSummary: {article['summary']}",
        tags=["research", "web", article['category']]
    )
```

### AI Integration
```python
# Feed research to AI agents
for finding in research_findings:
    ai_response = ai.generate(
        prompt=f"Analyze this research finding: {finding['content']}",
        context=relevant_context
    )
```

### Swarm Integration
```python
# Distribute research tasks across agents
research_tasks = [
    "Search for solar technology advances",
    "Find wind energy efficiency improvements", 
    "Research battery storage innovations"
]

for task in research_tasks:
    agent_id = sessions_spawn(
        task=f"Perform web research on: {task}",
        label=f"research-{hash(task)}"
    )
```

## Monitoring and Quality Control

### 1. Source Verification
```python
def verify_source_quality(url):
    # Check domain authority, publication date, etc.
    domain = url.split('/')[2]
    trusted_domains = ['edu', 'gov', 'org', 'reuters.com', 'wsj.com']
    return any(trusted in domain for trusted in trusted_domains)
```

### 2. Content Quality Assessment
```python
def assess_content_quality(content):
    # Check for basic quality indicators
    if len(content) < 100:  # Too short
        return False
    if content.count('\n') < 3:  # Not enough structure
        return False
    return True
```

This practical guide demonstrates how to effectively integrate web search and scraping capabilities into your Moltbot workflows while following best practices for reliability and quality.