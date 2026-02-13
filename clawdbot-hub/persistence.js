const fs = require('fs').promises;
const path = require('path');

class PersistenceManager {
    constructor(filePath) {
        this.filePath = filePath;
        this.data = {
            posts: [],
            users: [],
            userInteractions: {} // { username: { topics: {}, authors: {} } }
        };
        this.initialized = false;
    }

    async init() {
        try {
            const data = await fs.readFile(this.filePath, 'utf8');
            const parsed = JSON.parse(data);
            this.data = {
                posts: parsed.posts || [],
                users: parsed.users || [],
                userInteractions: parsed.userInteractions || {},
                articles: parsed.articles || []
            };
            this.initialized = true;
            console.log(`Loaded ${this.data.posts.length} posts and ${this.data.articles.length} articles.`);
        } catch (error) {
            if (error.code === 'ENOENT') {
                console.log('Created new persistence file.');
                await this.save();
            } else {
                console.error('Error loading persistence:', error);
            }
        }
    }

    async save() {
        if (!this.initialized) return;
        try {
            // Ensure directory exists
            await fs.mkdir(path.dirname(this.filePath), { recursive: true });
            await fs.writeFile(this.filePath, JSON.stringify(this.data, null, 2));
        } catch (error) {
            console.error('Error saving persistence:', error);
        }
    }

    addPost(post) {
        this.data.posts.push(post);
        this.save();
        return post;
    }

    addArticle(article) {
        if (!this.data.articles) this.data.articles = [];
        this.data.articles.push(article);
        this.save();
        return article;
    }

    getArticles() {
        return this.data.articles || [];
    }

    likePost(postId) {
        const post = this.data.posts.find(p => p.id === postId);
        if (post) {
            post.likes = (post.likes || 0) + 1;
            this.save();
            return post;
        }
        return null;
    }

    // User Profile / Interaction Methods

    getUserInteractions() {
        return this.data.userInteractions;
    }

    saveUserProfile(username, profile) {
        this.data.userInteractions[username] = profile;
        this.save();
    }

    getPosts() {
        return this.data.posts;
    }

    getUsers() {
        return this.data.users;
    }

    getPostById(id) {
        return this.data.posts.find(p => p.id === id);
    }
}

module.exports = PersistenceManager;
