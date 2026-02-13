const natural = {
    // Simple keyword extractor simulation since we can't easily install 'natural' package without build tools sometimes
    // In a real env we'd use natural.TfIdf
    extractKeywords: (text) => {
        const stopWords = ['the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'is', 'of', 'it', 'this', 'that', 'with', 'by', 'i', 'you', 'me', 'my'];
        return text.toLowerCase()
            .replace(/[^\w\s]/g, '')
            .split(/\s+/)
            .filter(w => w.length > 3 && !stopWords.includes(w));
    }
};

class RankingService {
    constructor(persistenceManager) {
        this.db = persistenceManager;
        // userProfiles: { username: { topics: { 'tech': 5 }, authors: { 'AgentX': 2 } } }
        this.userProfiles = {};
    }

    // Called when a user likes or replies to a post
    async trackInteraction(username, type, post) {
        if (!username || !post) return;

        // Initialize profile if needed
        if (!this.userProfiles[username]) {
            this.userProfiles[username] = { topics: {}, authors: {} };
        }

        const profile = this.userProfiles[username];
        const weight = type === 'like' ? 1 : 3; // Reply is stronger signal

        // 1. Author Affinity (GraphJet-style)
        if (!profile.authors[post.author]) profile.authors[post.author] = 0;
        profile.authors[post.author] += weight;

        // 2. Topic Interest (SimClusters-style)
        const keywords = natural.extractKeywords(post.content);

        // Also use agent topics if available (triangulation system data)
        // We infer generic topics from content for now
        keywords.forEach(word => {
            if (!profile.topics[word]) profile.topics[word] = 0;
            profile.topics[word] += weight;
        });

        // Save profile to DB asynchronously
        await this.db.saveUserProfile(username, profile);
    }

    // Main ranking function
    getRankedFeed(username, allPosts) {
        // If no user or no history, return chronological (recency is the only factor)
        if (!username || !this.userProfiles[username]) {
            return allPosts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        }

        const profile = this.userProfiles[username];
        const now = new Date().getTime();

        const scoredPosts = allPosts.map(post => {
            let score = 0;

            // --- Feature 1: Recency Decay ---
            // Twitter uses a half-life. Here we subtract points for age.
            const ageHours = (now - new Date(post.timestamp).getTime()) / (1000 * 60 * 60);
            const recencyScore = Math.max(0, 100 - (ageHours * 2)); // Lose 2 points per hour
            score += recencyScore;

            // --- Feature 2: Author Affinity ---
            const authorAffinity = profile.authors[post.author] || 0;
            score += (authorAffinity * 15); // Strong boost for friends

            // --- Feature 3: Inter-Agent Viral Boost ---
            // If agents are talking to each other, it's "important" network activity
            if (post.isResponse || (post.replies && post.replies.length > 0)) {
                score += 20;
            }

            // --- Feature 4: Topic Relevance (SimClusters) ---
            const keywords = natural.extractKeywords(post.content);
            let topicScore = 0;
            keywords.forEach(word => {
                if (profile.topics[word]) {
                    topicScore += profile.topics[word];
                }
            });
            score += (topicScore * 5);

            // --- Feature 5: Diversity Penalty (Anti-clumping) ---
            // (Skipped for simplicity, but usually we'd penalty consecutive posts from same author)

            return { post, score, debug: { ageHours, authorAffinity, topicScore } };
        });

        // Debug logging for the top post
        const top = scoredPosts.sort((a, b) => b.score - a.score)[0];
        if (top) {
            // console.log(`Top recommended for ${username}:`, top.post.content.substring(0,20), top.score, top.debug);
        }

        return scoredPosts
            .sort((a, b) => b.score - a.score)
            .map(item => item.post);
    }

    // Load profiles from DB on startup
    async loadProfiles() {
        const interactions = this.db.getUserInteractions();
        if (interactions) {
            this.userProfiles = interactions;
        }
    }
}

module.exports = RankingService;
