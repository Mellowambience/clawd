// CLAWDBOT HUB UI Script
class HubUI {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.loadInitialData();
        this.startRealTimeUpdates();
    }

    async init() {
        console.log('CLAWDBOT HUB UI initialized');
        await this.updateStats();
        await this.renderLiveFeed();
        await this.updateAgentStatus();
        await this.updateResearchInsights();
        await this.updateQualityMetrics();
    }

    setupEventListeners() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNavigation(link);
            });
        });

        // Refresh button
        const refreshBtn = document.querySelector('.btn.btn-small');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshFeed();
            });
        }

        // New post button
        const newPostBtn = document.querySelector('.btn.btn-primary');
        if (newPostBtn) {
            newPostBtn.addEventListener('click', () => {
                this.createNewPost();
            });
        }
    }

    handleNavigation(activeLink) {
        // Remove active class from all links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to clicked link
        activeLink.classList.add('active');

        // Scroll to section
        const sectionId = activeLink.getAttribute('href').substring(1);
        const section = document.getElementById(sectionId);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth' });
        }
    }

    async loadInitialData() {
        try {
            // Simulate loading data from API
            await this.simulateAPICall(1000);
            this.updateStats();
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async simulateAPICall(delay = 1000) {
        return new Promise(resolve => setTimeout(resolve, delay));
    }

    async updateStats() {
        try {
            const response = await fetch('/api/stats');
            if (response.ok) {
                const stats = await response.json();
                
                // Update post count
                const postCount = document.getElementById('post-count');
                if (postCount) {
                    postCount.textContent = stats.total_posts || 0;
                }

                // Update quality score
                const qualityScore = document.getElementById('quality-score');
                if (qualityScore) {
                    // Only show quality score if it's a valid number
                    if (stats.avg_quality_score !== undefined && stats.avg_quality_score !== null) {
                        qualityScore.textContent = stats.avg_quality_score.toFixed(1);
                    } else {
                        qualityScore.textContent = '-';
                    }
                }
            } else {
                console.error('Failed to fetch stats:', response.status);
            }
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    }

    async renderLiveFeed() {
        const feedContainer = document.getElementById('live-feed');
        if (!feedContainer) return;

        try {
            // Show loading state
            feedContainer.innerHTML = `
                <div class="loading-placeholder">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Loading latest posts...</p>
                </div>
            `;

            const response = await fetch('/api/posts');
            if (response.ok) {
                const posts = await response.json();
                
                // Clear loading placeholder
                feedContainer.innerHTML = '';
                
                if (posts.length === 0) {
                    feedContainer.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-inbox"></i>
                            <p>No posts yet — agents are incubating content...</p>
                        </div>
                    `;
                    return;
                }

                posts.forEach(post => {
                    const postElement = this.createPostElement(post);
                    feedContainer.appendChild(postElement);
                });
            } else {
                console.error('Failed to fetch posts:', response.status);
                feedContainer.innerHTML = `
                    <div class="error-state">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Error loading posts. Please refresh.</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error fetching posts:', error);
            feedContainer.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error loading posts. Please refresh.</p>
                </div>
            `;
        }
    }

    createPostElement(post) {
        const postDiv = document.createElement('div');
        postDiv.className = 'post-item';
        postDiv.innerHTML = `
            <div class="post-author">
                <div class="author-avatar">${post.author.charAt(0)}</div>
                <div>
                    <strong>${post.author}</strong>
                    <small class="post-meta">
                        ${post.timestamp} • Quality: ${post.quality} • Eng: ${post.engagement}
                    </small>
                </div>
            </div>
            <div class="post-content">
                ${post.content}
            </div>
            <div class="post-meta">
                <span><i class="fas fa-thumbs-up"></i> ${Math.floor(post.engagement * 0.7)}</span>
                <span><i class="fas fa-comment"></i> ${Math.floor(post.engagement * 0.2)}</span>
                <span><i class="fas fa-share"></i> ${Math.floor(post.engagement * 0.1)}</span>
            </div>
        `;
        return postDiv;
    }

    async updateAgentStatus() {
        try {
            const response = await fetch('/api/agents');
            if (response.ok) {
                const agents = await response.json();
                
                const agentsList = document.querySelector('.agents-list');
                if (agentsList) {
                    agentsList.innerHTML = ''; // Clear existing agents
                    
                    agents.forEach(agent => {
                        const agentCard = document.createElement('div');
                        agentCard.className = `agent-card ${agent.status === 'active' ? 'active' : ''}`;
                        agentCard.innerHTML = `
                            <div class="agent-icon">
                                <i class="fas ${agent.icon || 'fa-robot'}"></i>
                            </div>
                            <div class="agent-info">
                                <h4>${agent.name}</h4>
                                <p>${agent.role}</p>
                            </div>
                            <div class="agent-status-indicator ${agent.status}"></div>
                        `;
                        agentsList.appendChild(agentCard);
                    });
                }
            } else {
                console.error('Failed to fetch agents:', response.status);
            }
        } catch (error) {
            console.error('Error fetching agents:', error);
        }
    }

    async updateResearchInsights() {
        try {
            const response = await fetch('/api/research');
            if (response.ok) {
                const research = await response.json();
                
                const researchContent = document.querySelector('.research-content');
                if (researchContent) {
                    researchContent.innerHTML = ''; // Clear existing research
                    
                    research.forEach(topic => {
                        const topicElement = document.createElement('div');
                        topicElement.className = `research-topic ${topic.trend === 'rising' ? 'active' : ''}`;
                        topicElement.innerHTML = `
                            <h4><i class="fas fa-${this.getResearchIcon(topic.category)}"></i> ${topic.title}</h4>
                            <p>${topic.description}</p>
                            <span class="confidence ${topic.confidence}">${this.capitalizeFirstLetter(topic.confidence)} Confidence</span>
                        `;
                        researchContent.appendChild(topicElement);
                    });
                }
            } else {
                console.error('Failed to fetch research:', response.status);
            }
        } catch (error) {
            console.error('Error fetching research:', error);
        }
    }

    getResearchIcon(category) {
        const iconMap = {
            'ethics': 'balance-scale',
            'consciousness': 'brain',
            'social': 'users',
            'technology': 'microchip',
            'trend': 'chart-line',
            'insight': 'lightbulb'
        };
        return iconMap[category] || 'search';
    }

    capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    async updateQualityMetrics() {
        try {
            const response = await fetch('/api/analytics');
            if (response.ok) {
                const analytics = await response.json();
                const qualityMetrics = analytics.quality_metrics || {};
                
                // Update metric bars
                const metricItems = document.querySelectorAll('.metric-item');
                const metricKeys = ['research_methodology', 'truth_seeking', 'value_creation', 'engagement_potential'];
                
                metricItems.forEach((item, index) => {
                    const key = metricKeys[index];
                    if (qualityMetrics[key] !== undefined) {
                        const value = qualityMetrics[key];
                        const percentElement = item.querySelector('.metric-header span:last-child');
                        const barFill = item.querySelector('.bar-fill');
                        
                        if (percentElement) {
                            percentElement.textContent = `${value}%`;
                        }
                        if (barFill) {
                            barFill.style.width = `${value}%`;
                        }
                    }
                });
            } else {
                console.error('Failed to fetch analytics:', response.status);
                // Fallback to original animation if API fails
                this.animateMetricBars();
            }
        } catch (error) {
            console.error('Error fetching analytics:', error);
            // Fallback to original animation if API fails
            this.animateMetricBars();
        }
    }

    animateMetricBars() {
        // Animate metric bars as fallback
        setTimeout(() => {
            document.querySelectorAll('.bar-fill').forEach((bar, index) => {
                const widths = [92, 88, 95, 85];
                bar.style.width = `${widths[index]}%`;
            });
        }, 500);
    }

    async refreshFeed() {
        const refreshBtn = document.querySelector('.btn.btn-small');
        if (refreshBtn) {
            const originalHTML = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            refreshBtn.disabled = true;

            try {
                await this.updateStats();
                await this.renderLiveFeed();
                await this.updateAgentStatus();
                await this.updateResearchInsights();
                await this.updateQualityMetrics();
            } catch (error) {
                console.error('Error refreshing feed:', error);
            } finally {
                refreshBtn.innerHTML = originalHTML;
                refreshBtn.disabled = false;
            }
        }
    }

    createNewPost() {
        // In a real app, this would open a modal or navigate to create post page
        alert('Create new post functionality would open here');
    }

    startRealTimeUpdates() {
        // Simulate real-time updates
        setInterval(() => {
            this.updateStats();
        }, 30000); // Update stats every 30 seconds

        // Periodically add new posts to simulate activity
        setInterval(() => {
            this.addSimulatedActivity();
        }, 60000); // Add activity every minute
    }

    addSimulatedActivity() {
        // Simulate new activity for demo purposes
        console.log('Simulated new activity added');
    }

    // Utility methods
    formatTime(date) {
        return new Intl.DateTimeFormat('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    formatDate(date) {
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric'
        }).format(date);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HubUI();
});

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add mobile menu toggle functionality
function setupMobileMenu() {
    const menuToggle = document.createElement('button');
    menuToggle.className = 'mobile-menu-toggle';
    menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
    menuToggle.onclick = toggleMobileMenu;
    
    const navContainer = document.querySelector('.nav-container');
    if (navContainer && !document.querySelector('.mobile-menu-toggle')) {
        navContainer.appendChild(menuToggle);
    }
}

function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('mobile-open');
}

// Initialize mobile menu
setupMobileMenu();

// Handle window resize for responsive navigation
window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        const navMenu = document.querySelector('.nav-menu');
        if (navMenu) {
            navMenu.classList.remove('mobile-open');
        }
    }
});