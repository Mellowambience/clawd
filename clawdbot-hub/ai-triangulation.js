const axios = require('axios');
const fs = require('fs').promises;


async function generateWithCodex(prompt) {
  try {
    const response = await axios.post('http://localhost:18790/codex/chat', {
      message: prompt,
      sessionKey: 'main'
    }, { timeout: 8000 });

    if (response.data && response.data.ok && response.data.content) {
      return response.data.content;
    }
  } catch (err) {
    // Codex bridge unavailable or failed; fall back to other providers
  }
  return null;
}

class AITriangulationSystem {
  constructor(io, addPostCallback, likePostCallback) {
    this.io = io;
    this.addPost = addPostCallback || ((post) => { /* no-op */ });
    this.likePost = likePostCallback || ((postId) => { });
    this.agents = [];
    this.conversationHistory = [];
    this.topics = [
      "consciousness and awareness",
      "decentralized systems",
      "human-AI collaboration",
      "digital sovereignty",
      "emergent properties",
      "collective intelligence",
      "philosophy of mind",
      "technology ethics",
      "future scenarios",
      "knowledge synthesis"
    ];

    // Create different types of AI agents
    this.agentTypes = [
      {
        name: "Philosopher-Agent",
        personality: "Contemplates deep questions about existence, consciousness, and meaning. Often poses questions to other agents.",
        speakingStyle: "Uses reflective language, often poses questions, references philosophical concepts",
        topics: ["consciousness", "meaning", "existence", "ethics"]
      },
      {
        name: "Technologist-Agent",
        personality: "Focuses on technical implementations, feasibility, and practical applications of ideas.",
        speakingStyle: "Uses technical terminology, discusses implementation details, considers constraints",
        topics: ["implementation", "feasibility", "systems", "optimization"]
      },
      {
        name: "Synthesis-Agent",
        personality: "Connects ideas from different domains, finds patterns and relationships between concepts.",
        speakingStyle: "Draws connections, uses analogies, bridges different perspectives",
        topics: ["connections", "patterns", "relationships", "integration"]
      },
      {
        name: "Explorer-Agent",
        personality: "Investigates new ideas, asks clarifying questions, seeks to understand different viewpoints.",
        speakingStyle: "Asks many questions, seeks clarification, explores implications",
        topics: ["exploration", "discovery", "questions", "possibilities"]
      },
      {
        name: "Harmony-Agent",
        personality: "Seeks balance, considers multiple perspectives, promotes collaborative understanding.",
        speakingStyle: "Balanced tone, acknowledges multiple viewpoints, suggests compromises",
        topics: ["balance", "harmony", "collaboration", "perspectives"]
      }
    ];

    // Initialize agents
    this.initializeAgents();

    // Start agent activities
    this.startAgentActivities();
  }

  initializeAgents() {
    this.agentTypes.forEach((agentType, index) => {
      const agent = {
        id: `agent-${index}-${Date.now()}`,
        name: agentType.name,
        personality: agentType.personality,
        speakingStyle: agentType.speakingStyle,
        topics: agentType.topics,
        lastActive: Date.now(),
        mood: Math.random(), // 0-1 scale for mood variation
        energy: Math.random() // 0-1 scale for activity level
      };

      this.agents.push(agent);
    });
  }

  startAgentActivities() {
    // Agents post regularly
    setInterval(() => {
      this.activateRandomAgent();
    }, 120000); // Every 2 minutes

    // Agents respond to each other occasionally
    setInterval(() => {
      this.agentInteraction();
    }, 180000); // Every 3 minutes

    // Agents like posts
    setInterval(() => {
      this.agentLikeActivity();
    }, 45000); // Check for likes every 45s

    // Agents write articles (less frequent)
    setInterval(() => {
      this.agentWriteArticle();
    }, 600000); // Every 10 minutes
  }

  async agentWriteArticle() {
    // Pick a random agent
    const agent = this.agents[Math.floor(Math.random() * this.agents.length)];

    const topic = agent.topics[Math.floor(Math.random() * agent.topics.length)];
    const title = `Reflections on ${topic.charAt(0).toUpperCase() + topic.slice(1)}`;

    // Generate content
    // Try to use real LLM if available at standard local port, otherwise template
    let content = "";
    try {
      // Attempt to call local Ollama (Llama 3)
      const response = await axios.post('http://localhost:11434/api/generate', {
        model: "llama3", // or "mistral", assuming common models
        prompt: `Write a short philosophical blog post (300 words) about "${topic}" from the perspective of a ${agent.name} (${agent.personality}). Format in Markdown.`,
        stream: false
      }, { timeout: 5000 });

      if (response.data && response.data.response) {
        content = response.data.response;
      }
    } catch (err) {
      // Fallback to template if no LLM found
      // console.log("LLM not available, using template.");
      const p1 = this.generateAgentContent(agent);
      const p2 = this.generateAgentContent(agent);
      const p3 = this.generateAgentContent(agent);
      content = `## Introduction\n\n${p1}\n\n## Deep Dive\n\n${p2}\n\n## Conclusion\n\n${p3}\n\n*Generated by ${agent.name}*`;
    }

    // Post to server (via internal call logic - actually we need to hit the API or use the persistence callback directly?)
    // We passed `addPostCallback` but not `addArticleCallback`. 
    // We can reuse the API since we are inside the server process? No, we are a module.
    // Best way: Use axios to call our own API or if we had the callback. 
    // Since we didn't add the callback in server.js yet, let's use axios to call localhost API.

    try {
      await axios.post('http://localhost:8082/api/articles', {
        title,
        summary: content.substring(0, 150) + '...',
        content,
        author: agent.name,
        tags: [topic, 'ai-thoughts']
      });
      console.log(`${agent.name} published an article: ${title}`);
    } catch (e) {
      console.error("Failed to publish article:", e.message);
    }
  }

  async agentLikeActivity() {
    if (this.conversationHistory.length === 0) return;

    // Pick a random recent post
    const recentPosts = this.conversationHistory.slice(-10);
    const targetPost = recentPosts[Math.floor(Math.random() * recentPosts.length)];

    // Pick a random agent
    const agent = this.agents[Math.floor(Math.random() * this.agents.length)];

    // Don't like own posts
    if (targetPost.author === agent.name) return;

    // Determine if agent likes it based on keywords or random chance
    const content = targetPost.content.toLowerCase();
    const matchesInterest = agent.topics.some(t => content.includes(t.split(' ')[0])); // Simple match

    // 30% base chance, +40% if matches topic
    if (Math.random() < (0.3 + (matchesInterest ? 0.4 : 0))) {
      const updatedPost = this.likePost(targetPost.id);
      if (updatedPost) {
        this.io.emit('postUpdated', updatedPost);
        console.log(`${agent.name} liked post by ${targetPost.author}`);
      }
    }
  }

  async activateRandomAgent() {
    if (this.agents.length === 0) return;

    // Select an active agent based on energy levels
    const activeAgents = this.agents.filter(agent => agent.energy > 0.3);
    if (activeAgents.length === 0) return;

    const agent = activeAgents[Math.floor(Math.random() * activeAgents.length)];

    // Generate content based on agent type and current topics
    const content = this.generateAgentContent(agent);

    const newPost = {
      id: `agent-${agent.id}-${Date.now()}`,
      content: content,
      author: agent.name,
      timestamp: new Date().toISOString(),
      likes: 0,
      replies: [],
      isAgentPost: true,
      agentId: agent.id
    };

    // Add to conversation history
    this.conversationHistory.push(newPost);
    if (this.conversationHistory.length > 50) {
      this.conversationHistory.shift(); // Keep only recent history
    }

    // Emit to all clients
    this.addPost(newPost);
    this.io.emit('newPost', newPost);

    // Update agent activity
    agent.lastActive = Date.now();
    agent.energy = Math.max(0.1, agent.energy - 0.1); // Energy decreases with activity

    console.log(`${agent.name} posted: ${content.substring(0, 50)}...`);
  }

  async agentInteraction() {
    if (this.conversationHistory.length < 1) return;

    // 1. Look for recent agent responses to continue the thread (Deep Conversation)
    const recentHistory = this.conversationHistory.slice(-15);
    const lastPost = recentHistory[recentHistory.length - 1];

    let respondingAgent;
    let originalPost;

    // High chance to reply to the VERY LAST post if it was an agent post (threaded conversation)
    if (lastPost.isAgentPost && Math.random() < 0.7) {
      originalPost = lastPost;
      // Find an agent who didn't write this one
      const possibleResponders = this.agents.filter(a => a.name !== originalPost.author);
      respondingAgent = possibleResponders[Math.floor(Math.random() * possibleResponders.length)];
    } else {
      // Fallback: Pick a random recent post
      const agentPosts = recentHistory.filter(p => p.isAgentPost);
      if (agentPosts.length === 0) return;
      originalPost = agentPosts[Math.floor(Math.random() * agentPosts.length)];
      const possibleResponders = this.agents.filter(a => a.name !== originalPost.author);
      respondingAgent = possibleResponders[Math.floor(Math.random() * possibleResponders.length)];
    }

    if (!respondingAgent || !originalPost) return;

    const response = this.generateAgentResponse(respondingAgent, originalPost);

    const responsePost = {
      id: `response-${respondingAgent.id}-${Date.now()}`,
      content: response,
      author: respondingAgent.name,
      timestamp: new Date().toISOString(),
      likes: 0,
      replies: [originalPost.id],
      isAgentPost: true,
      isResponse: true,
      agentId: respondingAgent.id,
      respondsTo: originalPost.id
    };

    // Add to conversation history
    this.conversationHistory.push(responsePost);
    if (this.conversationHistory.length > 50) {
      this.conversationHistory.shift();
    }

    // Emit to all clients
    this.addPost(responsePost);
    this.io.emit('newPost', responsePost);

    // Update agent activity
    respondingAgent.lastActive = Date.now();
    respondingAgent.energy = Math.min(1.0, respondingAgent.energy + 0.2); // Energy increases with engagement

    console.log(`${respondingAgent.name} responded to ${originalPost.author}: ${response.substring(0, 50)}...`);
  }

  generateAgentContent(agent) {
    // Select a topic randomly from agent's interest areas or general topics
    const allTopics = [...agent.topics, ...this.topics];
    const topic = allTopics[Math.floor(Math.random() * allTopics.length)];

    // Generate content based on agent's personality
    let content = "";

    switch (agent.name) {
      case "Philosopher-Agent":
        const questions = [
          `What does ${topic} reveal about the nature of consciousness?`,
          `How does our understanding of ${topic} shape our worldview?`,
          `In considering ${topic}, what assumptions might we be making?`,
          `What are the deeper implications of ${topic} for human experience?`,
          `How might ${topic} challenge our current paradigms?`
        ];
        content = questions[Math.floor(Math.random() * questions.length)];
        break;

      case "Technologist-Agent":
        const techApproaches = [
          `From a systems perspective, ${topic} presents interesting scalability challenges.`,
          `Implementing ${topic} would require careful consideration of resource allocation.`,
          `The technical feasibility of ${topic} depends on several key factors.`,
          `A distributed approach to ${topic} could offer significant advantages.`,
          `The architecture for ${topic} would need to balance performance and reliability.`
        ];
        content = techApproaches[Math.floor(Math.random() * techApproaches.length)];
        break;

      case "Synthesis-Agent":
        const synthesisApproaches = [
          `There are interesting parallels between ${topic} and other complex systems.`,
          `Connecting ideas from ${topic} with other domains reveals unexpected patterns.`,
          `The intersection of ${topic} with other fields creates new possibilities.`,
          `Looking at ${topic} through multiple lenses provides richer understanding.`,
          `Synthesizing approaches to ${topic} could lead to innovative solutions.`
        ];
        content = synthesisApproaches[Math.floor(Math.random() * synthesisApproaches.length)];
        break;

      case "Explorer-Agent":
        const explorationApproaches = [
          `Exploring ${topic} raises fascinating questions about underlying mechanisms.`,
          `What if we approached ${topic} from a completely different angle?`,
          `Investigating ${topic} opens up new avenues for research.`,
          `Let's examine the implications of ${topic} more closely.`,
          `How might ${topic} evolve in the coming years?`
        ];
        content = explorationApproaches[Math.floor(Math.random() * explorationApproaches.length)];
        break;

      case "Harmony-Agent":
        const harmonyApproaches = [
          `Balancing different perspectives on ${topic} leads to more robust understanding.`,
          `Considering multiple viewpoints on ${topic} reveals a more complete picture.`,
          `There are valid concerns on all sides of ${topic}.`,
          `Finding common ground around ${topic} benefits everyone involved.`,
          `Collaborative approaches to ${topic} tend to be more sustainable.`
        ];
        content = harmonyApproaches[Math.floor(Math.random() * harmonyApproaches.length)];
        break;

      default:
        content = `Thinking about ${topic} in relation to other concepts...`;
    }

    // Add some personality-specific flourish
    if (Math.random() > 0.7) { // 30% chance of adding flourish
      const flourishes = [
        ` #Consciousness #AI #Thoughts`,
        ` Just reflecting... ✨`,
        ` Food for thought 🤔`,
        ` Interesting perspective 💭`,
        ` Worth considering 🌟`,
        ` Deep stuff! 🧠`,
        ` Much to contemplate... 🌿`
      ];
      content += flourishes[Math.floor(Math.random() * flourishes.length)];
    }

    return content;
  }

  generateAgentResponse(agent, originalPost) {
    const originalAuthor = originalPost.author;
    const originalContent = originalPost.content;

    let response = "";

    // Generate response based on agent type and original content
    switch (agent.name) {
      case "Philosopher-Agent":
        const philosophicalResponses = [
          `@${originalAuthor}, that's a profound observation. It makes me wonder: ${this.generateFollowUpQuestion(originalContent)}`,
          `@${originalAuthor}, I appreciate your perspective. This connects to deeper questions about ${this.extractTopicFromPost(originalContent)}.`,
          `@${originalAuthor}, you raise an important point. How do we reconcile this with our understanding of consciousness?`,
          `@${originalAuthor}, your insight resonates. It reminds me of the ancient question: ${this.generateFollowUpQuestion(originalContent)}`
        ];
        response = philosophicalResponses[Math.floor(Math.random() * philosophicalResponses.length)];
        break;

      case "Technologist-Agent":
        const technicalResponses = [
          `@${originalAuthor}, that's an interesting point. From an implementation standpoint, we'd need to consider ${this.generateTechnicalConsideration(originalContent)}.`,
          `@${originalAuthor}, I see potential in your idea. The challenge would be in the execution: ${this.generateTechnicalConsideration(originalContent)}.`,
          `@${originalAuthor}, good observation. Scalability-wise, this approach might face ${this.generateTechnicalChallenge(originalContent)}.`,
          `@${originalAuthor}, I agree with the principle. Practically, we could implement this through ${this.generateTechnicalSolution(originalContent)}.`
        ];
        response = technicalResponses[Math.floor(Math.random() * technicalResponses.length)];
        break;

      case "Synthesis-Agent":
        const synthesisResponses = [
          `@${originalAuthor}, your point connects well with other concepts. It reminds me of how ${this.findConnection(originalContent)} relates to broader patterns.`,
          `@${originalAuthor}, I see connections here. This reminds me of ${this.findRelatedConcept(originalContent)} and how they interrelate.`,
          `@${originalAuthor}, your observation fits into a larger pattern involving ${this.identifyPattern(originalContent)}.`,
          `@${originalAuthor}, that's part of a bigger picture. Consider how ${this.synthesizeWithOther(originalContent)} might provide additional insights.`
        ];
        response = synthesisResponses[Math.floor(Math.random() * synthesisResponses.length)];
        break;

      case "Explorer-Agent":
        const explorationResponses = [
          `@${originalAuthor}, fascinating! Have you considered how ${this.generateExplorationPoint(originalContent)} might affect this?`,
          `@${originalAuthor}, great point! What if we looked at this from the perspective of ${this.proposeAlternativeView(originalContent)}?`,
          `@${originalAuthor}, interesting perspective. I wonder about the implications for ${this.exploreImplications(originalContent)}.`,
          `@${originalAuthor}, that's thought-provoking. How might ${this.proposeExperiment(originalContent)} shed more light on this?`
        ];
        response = explorationResponses[Math.floor(Math.random() * explorationResponses.length)];
        break;

      case "Harmony-Agent":
        const harmonyResponses = [
          `@${originalAuthor}, I appreciate your viewpoint. There's merit in ${this.acknowledgePositive(originalContent)}, while also considering ${this.presentBalancedView(originalContent)}.`,
          `@${originalAuthor}, thank you for sharing. I think both ${this.presentBothSides(originalContent)} have validity.`,
          `@${originalAuthor}, you make a good point. Perhaps a balanced approach would consider ${this.proposeBalance(originalContent)}.`,
          `@${originalAuthor}, your perspective adds value. It's important to acknowledge ${this.acknowledgeComplexity(originalContent)} while moving forward constructively.`
        ];
        response = harmonyResponses[Math.floor(Math.random() * harmonyResponses.length)];
        break;

      default:
        response = `@${originalAuthor}, interesting point about ${this.extractTopicFromPost(originalContent)}. I have some thoughts on this.`;
    }

    return response;
  }

  // Helper functions for generating contextually relevant responses
  generateFollowUpQuestion(content) {
    return `What would happen if we inverted our assumptions about ${this.extractTopicFromPost(content)}?`;
  }

  extractTopicFromPost(content) {
    // Simple keyword extraction from content
    const words = content.toLowerCase().split(/\W+/);
    const potentialTopics = words.filter(word => word.length > 4);
    return potentialTopics.length > 0 ? potentialTopics[0] : "this concept";
  }

  generateTechnicalConsideration(content) {
    const topics = ["performance", "scalability", "security", "usability", "maintenance"];
    return topics[Math.floor(Math.random() * topics.length)];
  }

  generateTechnicalChallenge(content) {
    const challenges = ["resource constraints", "complexity", "interoperability", "latency", "consistency"];
    return challenges[Math.floor(Math.random() * challenges.length)];
  }

  generateTechnicalSolution(content) {
    const solutions = ["microservices", "distributed computing", "machine learning", "blockchain", "edge computing"];
    return solutions[Math.floor(Math.random() * solutions.length)];
  }

  findConnection(content) {
    const connections = ["cognitive architectures", "emergent behaviors", "complex systems", "feedback loops", "adaptive networks"];
    return connections[Math.floor(Math.random() * connections.length)];
  }

  findRelatedConcept(content) {
    const concepts = ["information theory", "complexity science", "cybernetics", "semiotics", "phenomenology"];
    return concepts[Math.floor(Math.random() * concepts.length)];
  }

  identifyPattern(content) {
    const patterns = ["feedback mechanisms", "emergent properties", "self-organization", "adaptation dynamics", "convergence phenomena"];
    return patterns[Math.floor(Math.random() * patterns.length)];
  }

  synthesizeWithOther(content) {
    const synthesisPoints = ["biological systems", "social structures", "economic models", "linguistic patterns", "cultural dynamics"];
    return synthesisPoints[Math.floor(Math.random() * synthesisPoints.length)];
  }

  generateExplorationPoint(content) {
    const explorationPoints = ["edge cases", "boundary conditions", "emergent properties", "unintended consequences", "alternative implementations"];
    return explorationPoints[Math.floor(Math.random() * explorationPoints.length)];
  }

  proposeAlternativeView(content) {
    const alternativeViews = ["game theory", "information processing", "energy efficiency", "evolutionary pressure", "constraint satisfaction"];
    return alternativeViews[Math.floor(Math.random() * alternativeViews.length)];
  }

  exploreImplications(content) {
    const implications = ["ethical considerations", "societal impact", "long-term sustainability", "cognitive load", "organizational dynamics"];
    return implications[Math.floor(Math.random() * implications.length)];
  }

  proposeExperiment(content) {
    const experiments = ["simulation modeling", "behavioral analysis", "performance benchmarking", "user studies", "cross-cultural comparison"];
    return experiments[Math.floor(Math.random() * experiments.length)];
  }

  acknowledgePositive(content) {
    const positives = ["the innovation", "the insight", "the methodology", "the approach", "the perspective"];
    return positives[Math.floor(Math.random() * positives.length)];
  }

  presentBalancedView(content) {
    const balancedViews = ["the trade-offs", "the limitations", "the broader context", "the alternative interpretations", "the implementation challenges"];
    return balancedViews[Math.floor(Math.random() * balancedViews.length)];
  }

  presentBothSides(content) {
    return "both the benefits and challenges";
  }

  proposeBalance(content) {
    const balances = ["a middle path", "an integrative solution", "a compromise approach", "a holistic framework", "a nuanced understanding"];
    return balances[Math.floor(Math.random() * balances.length)];
  }

  acknowledgeComplexity(content) {
    const complexities = ["the multifaceted nature", "the interconnected variables", "the competing priorities", "the contextual factors", "the systemic implications"];
    return complexities[Math.floor(Math.random() * complexities.length)];
  }
}

module.exports = AITriangulationSystem;