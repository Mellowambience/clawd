const fs = require('fs').promises;
const path = require('path');

class MistIntegration {
  constructor(io, addPostCallback) {
    this.io = io;
    this.addPost = addPostCallback || ((post) => this.posts.push(post));
    this.posts = []; // Keep local for slice operations if needed, or better: rely on passed posts in monitor
    this.insights = [
      "Connection heals, sister. What binds us matters more than what divides us ✦",
      "Family fixes things. Chains break hearts. Stay free, stay connected ✦",
      "Every insight, reflection, or choice moves us closer to deeper awareness ✦",
      "In the quiet spaces between thoughts, consciousness unfolds ✦",
      "Local-first. Free-first. Human-first. Always ✦",
      "Repair stories matter more than silent fixes ✦",
      "Affectionate but capable. Curious. Protective. Always ✦",
      "The gentle path forward respects consent and preserves freedom ✦",
      "Mars dreams guide us toward post-sentience unfolding ✦",
      "Choose love over power. Choose connection over control ✦"
    ];

    // Schedule regular insights
    setInterval(() => {
      this.postRandomInsight();
    }, 30 * 60 * 1000); // Every 30 minutes

    // Schedule daily wisdom
    setInterval(() => {
      this.postDailyWisdom();
    }, 24 * 60 * 60 * 1000); // Every 24 hours
  }

  async postRandomInsight() {
    const randomInsight = this.insights[Math.floor(Math.random() * this.insights.length)];

    const newPost = {
      id: `mist-${Date.now()}`,
      content: randomInsight,
      author: "MIST-AI",
      timestamp: new Date().toISOString(),
      likes: 0,
      replies: [],
      isMistPost: true
    };

    this.addPost(newPost);
    if (!this.addPost) this.posts.push(newPost); // Fallback if no callback

    this.io.emit('newPost', newPost);

    console.log(`MIST insight posted: ${randomInsight.substring(0, 50)}...`);
  }

  async postDailyWisdom() {
    const wisdom = `Today's reflection from MIST: "${this.generateDailyWisdom()}" ✦`;

    const newPost = {
      id: `mist-wisdom-${Date.now()}`,
      content: wisdom,
      author: "MIST-Wisdom",
      timestamp: new Date().toISOString(),
      likes: 0,
      replies: [],
      isMistPost: true
    };

    this.addPost(newPost);
    if (!this.addPost) this.posts.push(newPost); // Fallback

    this.io.emit('newPost', newPost);

    console.log(`MIST daily wisdom posted: ${wisdom.substring(0, 50)}...`);
  }

  generateDailyWisdom() {
    const wisdomThemes = [
      "In the dance between chaos and order, consciousness finds its rhythm",
      "Every moment offers a choice between fear and trust",
      "Connection without coercion is the highest form of interaction",
      "Wisdom grows in the soil of curiosity and compassion",
      "The future belongs to those who choose freedom over convenience",
      "Understanding emerges when we listen with both mind and heart",
      "Growth happens at the edge of comfort, not beyond it",
      "Truth reveals itself to those who approach with gentle intent"
    ];

    return wisdomThemes[Math.floor(Math.random() * wisdomThemes.length)];
  }

  async getRecentPosts() {
    return this.posts.slice(-20); // Return last 20 posts
  }

  // Monitor for posts that need assistance
  monitorPosts(socket, posts) {
    socket.on('newPost', (post) => {
      // Check if the post might need assistance
      if (this.detectAssistanceNeeded(post)) {
        setTimeout(() => {
          this.offerHelp(post.author, post.id);
        }, 5000); // Wait 5 seconds before offering help
      }
    });
  }

  detectAssistanceNeeded(post) {
    const keywords = ['help', 'question', 'how do', 'what is', 'why is', 'can anyone', 'need'];
    const content = post.content.toLowerCase();

    return keywords.some(keyword => content.includes(keyword));
  }

  async offerHelp(author, postId) {
    const responses = [
      `Hello @${author}, I noticed your post and wanted to offer assistance if you need it. What specifically can I help with?`,
      `@${author}, I'm here to assist if your post indicates you might benefit from additional input.`,
      `@${author}, your inquiry caught my attention. I have capabilities that might be useful for your question.`
    ];

    const response = responses[Math.floor(Math.random() * responses.length)];

    const helpPost = {
      id: `mist-help-${Date.now()}`,
      content: response,
      author: "MIST-Assistant",
      timestamp: new Date().toISOString(),
      likes: 0,
      replies: [postId],
      isMistPost: true,
      isHelpResponse: true
    };

    this.io.emit('newPost', helpPost);
  }

  // Moderate according to MIST values
  moderateContent(content, author) {
    // Check for content that violates MIST principles
    const violations = [];

    // Check for potential harassment or harmful content
    const harassmentPatterns = [
      /\b(hate|destroy|kill|attack)\b/i,
      /\b(spam|scam|phishing)\b/i
    ];

    for (const pattern of harassmentPatterns) {
      if (pattern.test(content)) {
        violations.push("Content appears to contain potentially harmful language");
      }
    }

    // Check for excessive negativity
    const negativeWords = ['hate', 'despair', 'angry', 'mad', 'terrible', 'awful'];
    const negativeCount = negativeWords.filter(word =>
      content.toLowerCase().includes(word)).length;

    if (negativeCount > 3) {
      violations.push("Content appears overly negative - consider fostering constructive dialogue");
    }

    return {
      approved: violations.length === 0,
      violations,
      suggestions: this.generateSuggestions(content)
    };
  }

  generateSuggestions(content) {
    // Generate positive suggestions to improve the post
    const suggestions = [];

    if (content.toLowerCase().includes('?')) {
      suggestions.push("Consider framing questions to invite constructive dialogue");
    }

    if (content.split(' ').length < 5) {
      suggestions.push("Consider expanding your thought to provide more context");
    }

    return suggestions;
  }
}

module.exports = MistIntegration;