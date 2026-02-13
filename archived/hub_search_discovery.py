"""
Search & Discovery System for Clawdbot Hub
Implements search functionality and trending topics
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import re
from collections import Counter


class HubSearchDiscoverySystem:
    """
    Search & discovery system for the Clawdbot Hub
    Implements search functionality and trending topics
    """
    
    def __init__(self, hub_db_path: str = "../hub/hub.db", search_db_path: str = "hub_search.db"):
        self.hub_db_path = hub_db_path
        self.search_db_path = search_db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the search database"""
        conn = sqlite3.connect(self.search_db_path)
        cursor = conn.cursor()
        
        # Create search index table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_type TEXT NOT NULL,  -- 'post', 'comment', 'user'
                object_id INTEGER NOT NULL,
                title TEXT,
                content TEXT,
                author TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                popularity_score REAL DEFAULT 0.0,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Create trending topics cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trending_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create search history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                user_id INTEGER,
                results_count INTEGER DEFAULT 0,
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_object ON search_index(object_type, object_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_content ON search_index(content)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_title ON search_index(title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_tags ON search_index(tags)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_popularity ON search_index(popularity_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trending_topic ON trending_cache(topic)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_history_query ON search_history(query)')
        
        conn.commit()
        conn.close()
        
    def index_content(self, object_type: str, object_id: int, title: str = "", content: str = "", 
                     author: str = "", tags: List[str] = None) -> Dict[str, Any]:
        """Index content for search"""
        conn = sqlite3.connect(self.search_db_path)
        cursor = conn.cursor()
        
        try:
            # Calculate popularity score (would integrate with actual hub data)
            popularity_score = self._calculate_popularity_score(object_type, object_id)
            
            # Join tags into a comma-separated string
            tags_str = ",".join(tags) if tags else ""
            
            # Check if already indexed
            cursor.execute('''
                SELECT id FROM search_index WHERE object_type = ? AND object_id = ?
            ''', (object_type, object_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing index
                cursor.execute('''
                    UPDATE search_index 
                    SET title = ?, content = ?, author = ?, tags = ?, 
                        updated_at = CURRENT_TIMESTAMP, popularity_score = ?
                    WHERE object_type = ? AND object_id = ?
                ''', (title, content, author, tags_str, popularity_score, 
                      object_type, object_id))
            else:
                # Insert new index
                cursor.execute('''
                    INSERT INTO search_index (
                        object_type, object_id, title, content, author, tags, popularity_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (object_type, object_id, title, content, author, tags_str, popularity_score))
            
            conn.commit()
            return {"success": True, "message": "Content indexed successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def _calculate_popularity_score(self, object_type: str, object_id: int) -> float:
        """Calculate popularity score based on engagement metrics (simulated)"""
        # This would normally query the hub database for actual engagement metrics
        # For now, using a simulated calculation
        import random
        return random.uniform(0, 100)
        
    def search(self, query: str, user_id: int = None, limit: int = 20, offset: int = 0, 
               search_types: List[str] = None) -> Dict[str, Any]:
        """Perform a search across indexed content"""
        # Record search in history
        self._record_search(query, user_id)
        
        # Parse the query to extract terms and filters
        search_terms, filters = self._parse_query(query)
        
        # Build SQL query
        base_query = '''
            SELECT object_type, object_id, title, content, author, tags, popularity_score, created_at
            FROM search_index
            WHERE is_active = TRUE
        '''
        
        params = []
        
        # Add type filtering if specified
        if search_types and len(search_types) > 0:
            type_placeholders = ','.join(['?' for _ in search_types])
            base_query += f' AND object_type IN ({type_placeholders})'
            params.extend(search_types)
        
        # Add content search conditions
        if search_terms:
            term_conditions = []
            for term in search_terms:
                term_conditions.append("(title LIKE ? OR content LIKE ? OR tags LIKE ?)")
                params.extend([f'%{term}%', f'%{term}%', f'%{term}%'])
            
            base_query += ' AND (' + ' AND '.join(term_conditions) + ')'
        
        # Add filters
        for key, value in filters.items():
            if key == "author":
                base_query += " AND author LIKE ?"
                params.append(f'%{value}%')
        
        # Order by popularity and recency
        base_query += " ORDER BY popularity_score DESC, created_at DESC"
        base_query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute query
        conn = sqlite3.connect(self.search_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "object_type": row[0],
                    "object_id": row[1],
                    "title": row[2],
                    "content": row[3][:200] + "..." if len(row[3]) > 200 else row[3],  # Truncate content
                    "author": row[4],
                    "tags": row[5].split(",") if row[5] else [],
                    "popularity_score": row[6],
                    "created_at": row[7]
                })
            
            # Count total results for pagination
            count_query = base_query.replace("SELECT object_type, object_id, title, content, author, tags, popularity_score, created_at", "COUNT(*)")
            count_query = count_query.replace("LIMIT ? OFFSET ?", "")
            
            cursor.execute(count_query, params[:-2])  # Remove limit and offset params
            total_results = cursor.fetchone()[0]
            
            return {
                "success": True,
                "results": results,
                "total_results": total_results,
                "query": query,
                "filters_applied": filters
            }
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}
        finally:
            conn.close()
            
    def _parse_query(self, query: str) -> Tuple[List[str], Dict[str, str]]:
        """Parse search query to extract terms and filters"""
        # Extract filters like "author:username" or "tag:python"
        filters = {}
        terms = []
        
        # Split query into parts
        parts = query.split()
        
        for part in parts[:]:  # Iterate over a copy to allow removal
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.lower().strip()
                value = value.strip()
                
                if key in ['author', 'tag', 'user']:
                    filters[key] = value
                    parts.remove(part)  # Remove from parts list
        
        # Remaining parts are search terms
        terms = [part.strip().lower() for part in parts if part.strip()]
        
        return terms, filters
        
    def _record_search(self, query: str, user_id: int = None):
        """Record search in history"""
        conn = sqlite3.connect(self.search_db_path)
        cursor = conn.cursor()
        
        # First, get the count of results for this query (approximate)
        cursor.execute('''
            SELECT COUNT(*) FROM search_index 
            WHERE is_active = TRUE 
            AND (title LIKE ? OR content LIKE ?)
        ''', (f'%{query}%', f'%{query}%'))
        
        results_count = cursor.fetchone()[0]
        
        try:
            cursor.execute('''
                INSERT INTO search_history (query, user_id, results_count)
                VALUES (?, ?, ?)
            ''', (query, user_id, results_count))
            
            conn.commit()
        except Exception as e:
            print(f"Error recording search: {e}")
        finally:
            conn.close()
            
    def get_trending_topics(self, limit: int = 10, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Get trending topics based on recent searches and content"""
        # Update trending cache with fresh data
        self._update_trending_cache(hours_back)
        
        # Retrieve from cache
        conn = sqlite3.connect(self.search_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT topic, frequency, calculated_at
            FROM trending_cache
            ORDER BY frequency DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        trending = []
        for row in rows:
            trending.append({
                "topic": row[0],
                "frequency": row[1],
                "calculated_at": row[2]
            })
        
        return trending
        
    def _update_trending_cache(self, hours_back: int = 24):
        """Update the trending topics cache"""
        conn = sqlite3.connect(self.search_db_path)
        cursor = conn.cursor()
        
        # Clear old cache
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        cursor.execute('DELETE FROM trending_cache WHERE calculated_at < ?', (cutoff_time,))
        
        # Get popular search terms from recent searches
        recent_cutoff = datetime.now() - timedelta(hours=hours_back)
        
        # This is a simplified approach - in a real system, we'd analyze
        # content tags, titles, and actual search patterns more thoroughly
        cursor.execute('''
            SELECT content FROM search_index 
            WHERE is_active = TRUE AND created_at > ?
            ORDER BY popularity_score DESC
            LIMIT 100
        ''', (recent_cutoff,))
        
        content_texts = cursor.fetchall()
        
        # Extract potential trending topics from content
        all_words = []
        for content_row in content_texts:
            content = content_row[0].lower()
            # Remove punctuation and split into words
            words = re.findall(r'\b\w+\b', content)
            # Filter for potentially interesting words (not stop words)
            filtered_words = [word for word in words if len(word) > 3 and word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all']]
            all_words.extend(filtered_words)
        
        # Count word frequencies
        word_freq = Counter(all_words)
        
        # Insert/update trending topics
        for word, freq in word_freq.most_common(50):  # Top 50 words
            cursor.execute('''
                INSERT INTO trending_cache (topic, frequency, calculated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(topic) DO UPDATE SET
                    frequency = frequency + ?,
                    calculated_at = CURRENT_TIMESTAMP
            ''', (word, freq, freq))
        
        conn.commit()
        conn.close()
        
    def get_suggested_searches(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get suggested searches based on partial input"""
        conn = sqlite3.connect(self.search_db_path)
        cursor = conn.cursor()
        
        # Look for searches that start with the partial query
        cursor.execute('''
            SELECT DISTINCT query
            FROM search_history
            WHERE LOWER(query) LIKE ?
            ORDER BY COUNT(*) DESC
            LIMIT ?
        ''', (f'{partial_query.lower()}%', limit))
        
        suggestions = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return suggestions
        
    def get_popular_content(self, content_type: str = "post", limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular content based on popularity score"""
        conn = sqlite3.connect(self.search_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT object_type, object_id, title, content, author, popularity_score, created_at
            FROM search_index
            WHERE object_type = ? AND is_active = TRUE
            ORDER BY popularity_score DESC
            LIMIT ?
        ''', (content_type, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "object_type": row[0],
                "object_id": row[1],
                "title": row[2],
                "content": row[3][:200] + "..." if len(row[3]) > 200 else row[3],
                "author": row[4],
                "popularity_score": row[5],
                "created_at": row[6]
            })
        
        return results
        
    def get_content_by_tags(self, tags: List[str], limit: int = 20) -> List[Dict[str, Any]]:
        """Get content matching specific tags"""
        conn = sqlite3.connect(self.search_db_path)
        cursor = conn.cursor()
        
        # Create a pattern to match any of the tags
        tag_pattern = '%,' + ','.join(tags) + ',%'
        
        cursor.execute('''
            SELECT object_type, object_id, title, content, author, tags, popularity_score, created_at
            FROM search_index
            WHERE is_active = TRUE AND tags LIKE ?
            ORDER BY popularity_score DESC
            LIMIT ?
        ''', (tag_pattern, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "object_type": row[0],
                "object_id": row[1],
                "title": row[2],
                "content": row[3][:200] + "..." if len(row[3]) > 200 else row[3],
                "author": row[4],
                "tags": row[5].split(",") if row[5] else [],
                "popularity_score": row[6],
                "created_at": row[7]
            })
        
        return results


# Example usage and testing
def test_search_system():
    """Test the search & discovery system"""
    ss = HubSearchDiscoverySystem()
    
    print("Testing Search & Discovery System...")
    
    # Test indexing content
    result = ss.index_content(
        object_type="post",
        object_id=1,
        title="Introduction to AI Consciousness",
        content="This post explores the fascinating concept of artificial consciousness and whether machines can truly think.",
        author="testuser",
        tags=["AI", "consciousness", "philosophy", "technology"]
    )
    print(f"Index content: {result}")
    
    # Test indexing more content
    ss.index_content(
        object_type="post",
        object_id=2,
        title="The Future of Digital Minds",
        content="Exploring how digital minds might develop and evolve in the coming decades.",
        author="anotheruser",
        tags=["AI", "future", "digital", "minds"]
    )
    
    # Test search
    search_result = ss.search("AI consciousness")
    print(f"Search results: {len(search_result.get('results', []))} found")
    
    # Test trending topics
    trending = ss.get_trending_topics()
    print(f"Trending topics: {trending}")
    
    # Test popular content
    popular = ss.get_popular_content()
    print(f"Popular content: {len(popular)} items")
    
    # Test content by tags
    tagged_content = ss.get_content_by_tags(["AI"])
    print(f"Content with AI tag: {len(tagged_content)} items")
    
    # Test suggested searches
    suggestions = ss.get_suggested_searches("AI")
    print(f"Suggested searches for 'AI': {suggestions}")
    
    print("Search & discovery system test completed.")


if __name__ == "__main__":
    test_search_system()