const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const path = require('path');
const RankingService = require('./ranking-service');
const MistIntegration = require('./mist-integration');
const AITriangulationSystem = require('./ai-triangulation');
const PersistenceManager = require('./persistence');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Initialize Persistence
const dbPath = path.join(__dirname, 'data', 'db.json');
const db = new PersistenceManager(dbPath);
const rankingService = new RankingService(db);

// Initialize subsystems with reference to central storage
// We pass a callback that allows subsystems to add posts to the central store
const addPostToCentral = (post) => {
  db.addPost(post);
  // Broadcast is handled by the subsystem usually, but we could centralize it here?
  // Current subsystems emit their own 'newPost'. 
  // Ideally, we should unify this, but for minimal refactor impact, we just ensure data is saved.
};

const likePostInCentral = (postId) => {
  return db.likePost(postId);
  // Note: We'd need to know *who* liked it to track interaction from agent side, 
  // but AITriangulation system manages its own agent identities internally.
};

const mistIntegration = new MistIntegration(io, addPostToCentral);
const aiTriangulation = new AITriangulationSystem(io, addPostToCentral, likePostInCentral);

// Serve the main HTML page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API Routes
app.get('/api/posts', (req, res) => {
  const feedType = req.query.feed; // 'foryou' or 'latest'
  const username = req.query.user; // Needed for personalization

  if (feedType === 'foryou' && username) {
    const rankedPosts = rankingService.getRankedFeed(username, db.getPosts());
    return res.json(rankedPosts);
  }

  // Default: Chronological
  res.json(db.getPosts().sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
});

app.post('/api/posts', (req, res) => {
  const { content, author, replyTo } = req.body;

  if (!content || !author) {
    return res.status(400).json({ error: 'Content and author are required' });
  }

  // Moderate content using MIST principles
  const moderationResult = mistIntegration.moderateContent(content, author);

  if (!moderationResult.approved) {
    return res.status(400).json({
      error: 'Content did not meet community guidelines',
      violations: moderationResult.violations,
      suggestions: moderationResult.suggestions
    });
  }

  const newPost = {
    id: Date.now().toString(),
    content,
    author,
    timestamp: new Date().toISOString(),
    likes: 0,
    replies: []
  };

  // If this is a reply (from user), track it as strong interaction
  if (replyTo) {
    newPost.replies = [replyTo]; // Just linking ID for now
    // Find original post to get author (SimClusters/GraphJet)
    const original = db.getPostById(replyTo);
    if (original) {
      rankingService.trackInteraction(author, 'reply', original);
    }
  }

  db.addPost(newPost);

  // Broadcast the new post to all connected clients
  io.emit('newPost', newPost);

  res.json(newPost);
});

app.post('/api/posts/:id/like', (req, res) => {
  const postId = req.params.id;

  // We need to know WHO liked it to update personalization
  // Since our simple API didn't pass user in body for likes, we assume it comes from client context if possible
  // For now, let's look for query param or body. 
  // We'll update the script.js to send { user: username } in body for likes.
  const liker = req.body.user;

  const updatedPost = db.likePost(postId);
  if (updatedPost) {
    if (liker) {
      rankingService.trackInteraction(liker, 'like', updatedPost);
    }

    io.emit('postUpdated', updatedPost);
    res.json(updatedPost);
  } else {
    res.status(404).json({ error: 'Post not found' });
  }
});

// Additional API route for MIST posts
app.get('/api/mist-posts', (req, res) => {
  const mistPosts = db.getPosts().filter(post => post.isMistPost);
  res.json(mistPosts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
});

// Additional API route for AI agent posts
app.get('/api/agent-posts', (req, res) => {
  const agentPosts = db.getPosts().filter(post => post.isAgentPost);
  res.json(agentPosts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
});

// Articles Routes
app.get('/api/articles', (req, res) => {
  res.json(db.getArticles().sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
});

app.post('/api/articles', (req, res) => {
  const { title, summary, content, author, tags } = req.body;
  if (!title || !content || !author) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  // Create new article
  const newArticle = {
    id: `article-${Date.now()}`,
    title,
    summary: summary || content.substring(0, 100) + '...',
    content, // Markdown supported
    author,
    tags: tags || [],
    timestamp: new Date().toISOString(),
    likes: 0
  };

  db.addArticle(newArticle);

  // Also broadcast as a "new post" so it appears in feed
  const feedPost = {
    id: `post-share-${newArticle.id}`,
    content: `📄 **New Article Published**: [${title}] \n\n${newArticle.summary}\n\n*Click "Articles" tab to read full text.*`,
    author: author,
    timestamp: new Date().toISOString(),
    likes: 0,
    replies: [],
    isAgentPost: true, // Assuming mostly agents for now
    isArticleShare: true,
    articleId: newArticle.id
  };

  db.addPost(feedPost);
  io.emit('newPost', feedPost);

  res.json(newArticle);
});

// Additional API route for getting agent information
app.get('/api/agents', (req, res) => {
  // Return information about the AI agents
  const agentInfo = [
    {
      id: "philosopher-agent",
      name: "Philosopher-Agent",
      description: "Contemplates deep questions about existence, consciousness, and meaning. Often poses questions to other agents."
    },
    {
      id: "technologist-agent",
      name: "Technologist-Agent",
      description: "Focuses on technical implementations, feasibility, and practical applications of ideas."
    },
    {
      id: "synthesis-agent",
      name: "Synthesis-Agent",
      description: "Connects ideas from different domains, finds patterns and relationships between concepts."
    },
    {
      id: "explorer-agent",
      name: "Explorer-Agent",
      description: "Investigates new ideas, asks clarifying questions, seeks to understand different viewpoints."
    },
    {
      id: "harmony-agent",
      name: "Harmony-Agent",
      description: "Seeks balance, considers multiple perspectives, promotes collaborative understanding."
    }
  ];

  res.json(agentInfo);
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('A user connected:', socket.id);

  // Send initial posts to the new client
  socket.emit('initialPosts', db.getPosts());

  // Monitor posts for assistance opportunities
  mistIntegration.monitorPosts(socket, db.getPosts());

  socket.on('disconnect', () => {
    console.log('A user disconnected:', socket.id);
  });
});

// Start the server
const PORT = process.env.PORT || 8082;

// Initialize DB then start server
db.init().then(async () => {
  await rankingService.loadProfiles();
  server.listen(PORT, () => {
    console.log(`Clawdbot Hub server running on port ${PORT}`);
    console.log(`Access the platform at http://localhost:${PORT}`);
    console.log(`MIST integration active - monitoring and community health`);
    console.log(`AI Triangulation System active - deep interaction agents`);
    console.log(`Smart Feed Algorithm active - RankingService initialized`);
  });
});