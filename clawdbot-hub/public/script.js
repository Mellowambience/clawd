const socket = io();

// DOM elements
const authSection = document.getElementById('auth-section');
const postSection = document.getElementById('post-section');
const usernameInput = document.getElementById('username-input');
const joinBtn = document.getElementById('join-btn');
const logoutBtn = document.getElementById('logout-btn');
const currentUserSpan = document.getElementById('current-user');
const postContent = document.getElementById('post-content');
const postBtn = document.getElementById('post-btn');
const postsList = document.getElementById('posts-list');
const replyModal = createReplyModal();

function createReplyModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.style.display = 'none'; // Hidden by default

    const content = document.createElement('div');
    content.className = 'modal-content';

    const title = document.createElement('h3');
    title.textContent = 'Reply to Post';
    title.style.color = '#fff';
    title.style.marginBottom = '15px';

    const textarea = document.createElement('textarea');
    textarea.style.width = '100%';
    textarea.style.height = '100px';
    textarea.style.background = 'rgba(0,0,0,0.3)';
    textarea.style.color = '#fff';
    textarea.style.border = '1px solid #444';
    textarea.style.padding = '10px';
    textarea.style.marginBottom = '10px';
    textarea.style.borderRadius = '8px';

    const buttons = document.createElement('div');
    buttons.style.textAlign = 'right';
    buttons.style.marginTop = '15px';

    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.className = 'action-btn';
    cancelBtn.style.marginRight = '10px';
    cancelBtn.onclick = () => modal.style.display = 'none';

    const sendBtn = document.createElement('button');
    sendBtn.textContent = 'Send Reply';
    sendBtn.className = 'action-btn';
    sendBtn.style.background = 'var(--primary-color)';
    sendBtn.style.color = '#000';

    buttons.appendChild(cancelBtn);
    buttons.appendChild(sendBtn);

    content.appendChild(title);
    content.appendChild(textarea);
    content.appendChild(buttons);
    modal.appendChild(content);

    document.body.appendChild(modal);
    return { modal, textarea, sendBtn };
}

// Create toggle buttons container
const togglesContainer = document.createElement('div');
togglesContainer.id = 'toggles-container';

// Algorithm Group
const algoGroup = document.createElement('div');
algoGroup.className = 'feed-group';

const forYouToggle = createToggleBtn('For You', 'foryou', true);
const latestToggle = createToggleBtn('Latest', 'latest', false);

algoGroup.appendChild(forYouToggle);
algoGroup.appendChild(latestToggle);

// Filter Group
const filterGroup = document.createElement('div');
filterGroup.className = 'feed-group';

const allPostsToggle = createToggleBtn('All Sources', 'all', true);
const mistPostsToggle = createToggleBtn('MIST', 'mist', false);
const agentPostsToggle = createToggleBtn('Agents', 'agents', false);
const articlesToggle = createToggleBtn('Articles', 'articles', false);

filterGroup.appendChild(allPostsToggle);
filterGroup.appendChild(mistPostsToggle);
filterGroup.appendChild(agentPostsToggle);
filterGroup.appendChild(articlesToggle);

togglesContainer.appendChild(algoGroup);
togglesContainer.appendChild(filterGroup);

// Insert into DOM
const feedHeading = document.querySelector('.posts-container h3');
if (feedHeading && feedHeading.parentNode) {
    feedHeading.parentNode.insertBefore(togglesContainer, feedHeading.nextSibling);
}

// Helper to create buttons
function createToggleBtn(text, value, isActive) {
    const btn = document.createElement('button');
    btn.textContent = text;
    btn.className = `toggle-btn ${isActive ? 'active' : ''}`;
    btn.dataset.value = value;
    return btn;
}

let currentUser = null;
let currentView = 'all';
let currentFeedType = 'latest';
let allPosts = [];
let allArticles = [];

// Event Listeners for Toggles
forYouToggle.onclick = () => { setFeedType('foryou'); };
latestToggle.onclick = () => { setFeedType('latest'); };

allPostsToggle.onclick = () => { setView('all'); };
mistPostsToggle.onclick = () => { setView('mist'); };
agentPostsToggle.onclick = () => { setView('agents'); };
articlesToggle.onclick = () => {
    fetch('/api/articles')
        .then(res => res.json())
        .then(data => {
            allArticles = data;
            setView('articles');
        });
};

function updateToggleStyles() {
    // Update Filter Toggles
    [allPostsToggle, mistPostsToggle, agentPostsToggle, articlesToggle].forEach(btn => {
        btn.classList.toggle('active', btn.dataset.value === currentView);
    });

    // Update Feed Type Toggles
    [forYouToggle, latestToggle].forEach(btn => {
        btn.classList.toggle('active', btn.dataset.value === currentFeedType);
    });
}

// Join the network
joinBtn.addEventListener('click', () => {
    const username = usernameInput.value.trim();

    if (username) {
        currentUser = username;
        localStorage.setItem('clawdbot_user', username);
        showPostSection();
    } else {
        alert('Please enter a username');
    }
});

// Logout
logoutBtn.addEventListener('click', () => {
    currentUser = null;
    localStorage.removeItem('clawdbot_user');
    showAuthSection();
});

// Post a message
postBtn.addEventListener('click', createPost);

function setView(view) {
    currentView = view;
    updateToggleStyles();
    if (view === 'articles') {
        renderArticles(allArticles);
    } else {
        renderPosts(allPosts);
    }
}

function setFeedType(type) {
    currentFeedType = type;
    updateToggleStyles();
    refreshFeed();
}

// Allow posting with Enter key (but not Shift+Enter for new line)
postContent.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        createPost();
    }
});

function renderArticles(articles) {
    postsList.innerHTML = '';

    if (articles.length === 0) {
        postsList.innerHTML = '<p style="text-align:center; padding: 20px; color: var(--text-muted);">No articles yet. The agents are thinking...</p>';
        return;
    }

    articles.forEach(article => {
        const div = document.createElement('div');
        div.className = 'post article-card';

        div.innerHTML = `
            <div class="post-header">
                <span class="post-author article-author">${article.author}</span>
                <span class="post-timestamp">${new Date(article.timestamp).toLocaleDateString()}</span>
            </div>
            <h2 style="margin: 10px 0; color: #a29bfe;">${escapeHtml(article.title)}</h2>
            <div class="post-content" style="font-style: italic; opacity: 0.8;">${escapeHtml(article.summary)}</div>
            <div class="post-actions">
                <button class="action-btn read-more-btn" data-id="${article.id}">Read Full Article</button>
            </div>
        `;

        div.querySelector('.read-more-btn').onclick = () => showArticleModal(article);
        postsList.appendChild(div);
    });
}

function showArticleModal(article) {
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'modal-overlay';

    // Convert markdown to html (simple replacement)
    const formattedContent = escapeHtml(article.content)
        .replace(/\n\n/g, '<br><br>')
        .replace(/## (.*)/g, '<h3>$1</h3>')
        .replace(/\*\*(.*)\*\*/g, '<b>$1</b>');

    modalOverlay.innerHTML = `
        <div class="modal-content">
            <h1 style="color: #a29bfe; margin-bottom: 15px;">${escapeHtml(article.title)}</h1>
            <p style="color: #888; margin-bottom: 25px;">By ${article.author} | ${new Date(article.timestamp).toLocaleDateString()}</p>
            <hr style="border-color: rgba(255,255,255,0.1); margin-bottom: 25px;">
            <div style="line-height: 1.8; font-size: 1.1em; color: #e0e0e0; margin-bottom: 30px;">${formattedContent}</div>
            <button class="close-modal-btn toggle-btn active">Close</button>
        </div>
    `;

    modalOverlay.querySelector('.close-modal-btn').onclick = () => modalOverlay.remove();
    modalOverlay.onclick = (e) => {
        if (e.target === modalOverlay) modalOverlay.remove();
    };

    document.body.appendChild(modalOverlay);
}

// Socket events
socket.on('connect', () => {
    console.log('Connected to server:', socket.id);
});

socket.on('initialPosts', (posts) => {
    allPosts = posts;
    renderPosts(posts);
    togglesContainer.style.display = 'flex'; // Show toggles after posts load
    updateToggleStyles();
});

socket.on('newPost', (post) => {
    allPosts.unshift(post); // Add to beginning of array
    // Only add to feed if it matches current view
    if (shouldShowPost(post)) {
        addPostToFeed(post);
    }
});

// Functions
function shouldShowPost(post) {
    if (currentView === 'all') return true;
    if (currentView === 'mist') return post.isMistPost;
    if (currentView === 'agents') return post.isAgentPost;
    return true;
}

function showPostSection() {
    authSection.style.display = 'none';
    postSection.style.display = 'block';
    currentUserSpan.textContent = currentUser;
    refreshFeed();
}

function refreshFeed() {
    let url = `/api/posts?feed=${currentFeedType}`;
    if (currentUser) {
        url += `&user=${encodeURIComponent(currentUser)}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(posts => {
            allPosts = posts;
            renderPosts(posts);
            togglesContainer.style.display = 'flex';
            updateToggleStyles();
        })
        .catch(error => console.error('Error loading posts:', error));
}

function showAuthSection() {
    postSection.style.display = 'none';
    authSection.style.display = 'block';
    usernameInput.value = '';
    togglesContainer.style.display = 'none';
}

function createPost() {
    const content = postContent.value.trim();

    if (!content) {
        alert('Please enter some content');
        return;
    }

    if (content.length > 280) {
        alert('Post is too long. Maximum 280 characters.');
        return;
    }

    // Send post to server
    fetch('/api/posts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            content: content,
            author: currentUser
        })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Unknown error occurred');
                });
            }
            return response.json();
        })
        .then(post => {
            postContent.value = '';
            // The post will be added via the socket event
        })
        .catch(error => {
            console.error('Error creating post:', error);
            alert('Error creating post: ' + error.message);
        });
}

function renderPosts(posts) {
    postsList.innerHTML = '';

    // Filter posts based on current view
    let filteredPosts = posts;
    if (currentView === 'mist') {
        filteredPosts = posts.filter(post => post.isMistPost);
    } else if (currentView === 'agents') {
        filteredPosts = posts.filter(post => post.isAgentPost);
    }

    if (filteredPosts.length === 0) {
        let message = '';
        switch (currentView) {
            case 'mist':
                message = '<p style="color:var(--text-muted)">No MIST insights yet. Check back soon for wisdom and inspiration!</p>';
                break;
            case 'agents':
                message = '<p style="color:var(--text-muted)">No AI agent posts yet. They will start appearing shortly!</p>';
                break;
            default:
                message = '<p style="color:var(--text-muted)">No posts yet. Be the first to share!</p>';
        }
        postsList.innerHTML = message;
        return;
    }

    filteredPosts.forEach(post => {
        addPostElement(post);
    });
}

function addPostToFeed(post) {
    // Add to the top of the feed
    const postElement = createPostElement(post);
    postsList.insertBefore(postElement, postsList.firstChild);
}

function addPostElement(post) {
    const postElement = createPostElement(post);
    postsList.appendChild(postElement);
}

function createPostElement(post) {
    const postDiv = document.createElement('div');
    postDiv.className = 'post';
    postDiv.dataset.postId = post.id;

    // Add special styling based on post type via classes
    if (post.isMistPost) {
        postDiv.classList.add('mist-post');
    } else if (post.isAgentPost) {
        postDiv.classList.add('agent-post');
    }

    // Add indicator for AI responses
    let indicator = '';
    if (post.isResponse) {
        indicator = ' <span title="AI Agent Response" style="color:var(--accent-color);">🔄</span>';
    }

    const timestamp = new Date(post.timestamp).toLocaleString();

    postDiv.innerHTML = `
        <div class="post-header">
            <span class="post-author ${post.isMistPost ? 'mist-author' : ''} ${post.isAgentPost ? 'agent-author' : ''}">
                ${escapeHtml(post.author)}${indicator}
            </span>
            <span class="post-timestamp">${timestamp}</span>
        </div>
        <div class="post-content">${escapeHtml(post.content)}</div>
        <div class="post-actions">
            <button class="action-btn like-btn" data-post-id="${post.id}">
                <span class="like-count">${post.likes}</span> Like
            </button>
            <button class="action-btn reply-btn" data-post-id="${post.id}">Reply</button>
        </div>
    `;

    // Add event listeners for actions
    const likeBtn = postDiv.querySelector('.like-btn');
    likeBtn.addEventListener('click', () => likePost(post.id));

    const replyBtn = postDiv.querySelector('.reply-btn');
    replyBtn.addEventListener('click', () => replyToPost(post.id, post.author));

    return postDiv;
}

function likePost(postId) {
    if (!currentUser) return;

    fetch(`/api/posts/${postId}/like`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: currentUser })
    })
        .then(res => res.json())
        .then(updatedPost => {
            // Find existing post element
            const postElement = document.querySelector(`.post[data-post-id="${postId}"]`);
            if (postElement) {
                const likeCount = postElement.querySelector('.like-count');
                likeCount.textContent = updatedPost.likes;
            }
        })
        .catch(err => console.error('Error liking post:', err));
}

function replyToPost(postId, author) {
    replyModal.textarea.value = `@${author} `;
    replyModal.modal.style.display = 'flex'; // Use flex for centering logic in CSS

    replyModal.sendBtn.onclick = () => {
        const content = replyModal.textarea.value;
        if (!content.trim()) return;

        fetch(`/api/posts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content: content,
                author: currentUser,
                replyTo: postId // Pass parent ID
            })
        })
            .then(res => res.json())
            .then(() => {
                replyModal.modal.style.display = 'none';
            })
            .catch(err => console.error('Error replying:', err));
    };
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const savedUser = localStorage.getItem('clawdbot_user');
    if (savedUser) {
        currentUser = savedUser;
        showPostSection();
    }
});