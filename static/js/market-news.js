// Market News JavaScript Module
let currentNewsData = [];
let updateInterval = null;

// Initialize market news when page loads
function initializeMarketNews() {
    loadMarketIndicators();
    loadMarketNews();
    loadRegionalData();
    loadTrendingTopics();
    loadMarketEvents();
    loadMarketCommentary();
    
    // Load saved articles count
    updateSavedArticleCount();
    
    // Set up auto-refresh
    startAutoRefresh();
    
    // Set up event listeners
    setupEventListeners();
    
    // Update last refresh time
    updateLastRefreshTime();
}

// Load market indicators
async function loadMarketIndicators() {
    try {
        const response = await fetch('/api/market-indicators');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateSentimentGauge(data.data.sentiment, data.data.sentiment_score);
            updateMarketMetrics(data.data);
            updateIndicators(data.data.indicators);
        }
    } catch (error) {
        console.error('Error loading market indicators:', error);
    }
}

// Load market news
async function loadMarketNews(filters = {}) {
    try {
        const params = new URLSearchParams({
            region: filters.region || 'all',
            asset: filters.asset || 'all',
            source: filters.source || 'all',
            search: filters.search || '',
            limit: 20
        });
        
        const response = await fetch(`/api/market-news?${params}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            currentNewsData = data.news;
            renderNewsItems(data.news);
        }
    } catch (error) {
        console.error('Error loading market news:', error);
    }
}

// Render news items
function renderNewsItems(newsItems) {
    const container = document.getElementById('newsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    newsItems.forEach(item => {
        const newsElement = createNewsElement(item);
        container.appendChild(newsElement);
    });
    
    // Add load more button
    if (newsItems.length >= 20) {
        const loadMoreBtn = document.createElement('div');
        loadMoreBtn.className = 'text-center mt-3';
        loadMoreBtn.innerHTML = `
            <button class="btn btn-outline-primary btn-sm" onclick="loadMoreNews()">
                <i class="fas fa-plus-circle me-2"></i>Load More Stories
            </button>
        `;
        container.appendChild(loadMoreBtn);
    }
}

// Create news element
function createNewsElement(item) {
    const div = document.createElement('div');
    div.className = 'news-item border-bottom border-secondary pb-3 mb-3';
    
    // Determine badge color based on type
    const badgeColors = {
        'BREAKING': 'danger',
        'MARKET MOVE': 'primary',
        'ANALYSIS': 'warning',
        'DEAL NEWS': 'success',
        'REGULATORY': 'info'
    };
    
    const badgeColor = badgeColors[item.type] || 'secondary';
    
    div.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-2">
            <span class="badge bg-${badgeColor}">${item.type}</span>
            <small class="text-muted">${item.time}</small>
        </div>
        <h6 class="text-white mb-2">${item.title}</h6>
        <p class="text-muted small mb-2">${item.content}</p>
        <div class="d-flex justify-content-between align-items-center">
            <small class="text-info">
                <i class="fas fa-tag me-1"></i>${item.tags.slice(0, 3).join(' • ')}
            </small>
            <small class="text-warning">
                <i class="fas fa-newspaper me-1"></i>${item.source}
            </small>
        </div>
    `;
    
    // Add click handler
    div.addEventListener('click', () => openNewsDetail(item));
    
    return div;
}

// Load regional data
async function loadRegionalData() {
    try {
        const response = await fetch('/api/market-regional');
        const data = await response.json();
        
        if (data.status === 'success') {
            renderRegionalData(data.regions);
        }
    } catch (error) {
        console.error('Error loading regional data:', error);
    }
}

// Render regional data
function renderRegionalData(regions) {
    const container = document.querySelector('.regional-analysis-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    regions.forEach(region => {
        const regionCard = createRegionCard(region);
        container.appendChild(regionCard);
    });
}

// Create region card
function createRegionCard(region) {
    const col = document.createElement('div');
    col.className = 'col-md-4 mb-3';
    
    const trendIcon = region.issuance_trend === 'up' ? '↑' : '↓';
    const trendClass = region.issuance_trend === 'up' ? 'text-success' : 'text-danger';
    
    const trendBadgeColor = {
        'Stable': 'success',
        'Volatile': 'warning',
        'Tightening': 'info'
    }[region.market_trend] || 'secondary';
    
    col.innerHTML = `
        <div class="region-card p-3 border border-secondary rounded">
            <h6 class="text-white mb-2">
                <img src="https://flagcdn.com/24x18/${region.flag}.png" class="me-2">${region.region}
            </h6>
            <div class="small">
                <div class="d-flex justify-content-between text-muted mb-1">
                    <span>${region.primary_asset} Issuance:</span>
                    <span class="${trendClass}">${region.issuance} ${trendIcon}</span>
                </div>
                <div class="d-flex justify-content-between text-muted mb-1">
                    <span>Avg Spread:</span>
                    <span class="text-warning">${region.avg_spread}</span>
                </div>
                <div class="d-flex justify-content-between text-muted">
                    <span>Market Trend:</span>
                    <span class="badge bg-${trendBadgeColor} bg-opacity-75">${region.market_trend}</span>
                </div>
            </div>
        </div>
    `;
    
    return col;
}

// Load trending topics
async function loadTrendingTopics() {
    try {
        const response = await fetch('/api/market-trending');
        const data = await response.json();
        
        if (data.status === 'success') {
            renderTrendingTopics(data.topics);
        }
    } catch (error) {
        console.error('Error loading trending topics:', error);
    }
}

// Render trending topics
function renderTrendingTopics(topics) {
    const container = document.querySelector('.trending-topics');
    if (!container) return;
    
    container.innerHTML = '';
    
    topics.forEach((topic, index) => {
        const badgeColor = index === 0 ? 'danger' : index === 1 ? 'warning' : index === 2 ? 'info' : 'secondary';
        const topicElement = document.createElement('a');
        topicElement.href = '#';
        topicElement.className = 'd-block text-decoration-none text-white mb-2';
        topicElement.innerHTML = `
            <span class="badge bg-${badgeColor} me-2">${topic.rank}</span>${topic.topic}
        `;
        topicElement.addEventListener('click', (e) => {
            e.preventDefault();
            searchNews(topic.topic);
        });
        container.appendChild(topicElement);
    });
}

// Load market events
async function loadMarketEvents() {
    try {
        const response = await fetch('/api/market-events');
        const data = await response.json();
        
        if (data.status === 'success') {
            renderMarketEvents(data.events);
        }
    } catch (error) {
        console.error('Error loading market events:', error);
    }
}

// Render market events
function renderMarketEvents(events) {
    const container = document.querySelector('.events-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    events.forEach((event, index) => {
        const eventDiv = document.createElement('div');
        eventDiv.className = index < events.length - 1 ? 'event-item mb-3 pb-3 border-bottom border-secondary' : 'event-item';
        
        const dateColor = event.date === 'Tomorrow' ? 'warning' : 'info';
        
        eventDiv.innerHTML = `
            <div class="d-flex justify-content-between mb-1">
                <small class="text-${dateColor}">${event.date}</small>
                <small class="text-muted">${event.time}</small>
            </div>
            <h6 class="text-white small mb-1">${event.title}</h6>
            <small class="text-muted">Impact: ${event.impact}</small>
        `;
        
        container.appendChild(eventDiv);
    });
}

// Market commentary state
let currentCommentaryPage = 0;
let commentaryExperts = [];
let frequentExperts = [];

// Load market commentary with pagination
async function loadMarketCommentary(page = 0) {
    try {
        const response = await fetch(`/api/market-commentary?page=${page}&per_page=2`);
        const data = await response.json();
        
        if (data.status === 'success') {
            currentCommentaryPage = data.page;
            commentaryExperts = data.experts;
            frequentExperts = data.frequent_experts;
            renderMarketCommentary(data.experts, data);
        }
    } catch (error) {
        console.error('Error loading market commentary:', error);
    }
}

// Render market commentary with navigation
function renderMarketCommentary(experts, metadata) {
    const container = document.querySelector('.commentary-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Create navigation header if there are multiple pages
    if (metadata.total > metadata.per_page) {
        const navHeader = document.createElement('div');
        navHeader.className = 'd-flex justify-content-between align-items-center mb-3';
        navHeader.innerHTML = `
            <div>
                <small class="text-muted">Showing ${metadata.page * metadata.per_page + 1}-${Math.min((metadata.page + 1) * metadata.per_page, metadata.total)} of ${metadata.total} experts</small>
            </div>
            <div>
                <button class="btn btn-sm btn-outline-secondary me-2" onclick="navigateCommentary('prev')" ${metadata.page === 0 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-left"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary" onclick="navigateCommentary('next')" ${!metadata.has_more ? 'disabled' : ''}>
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        `;
        container.appendChild(navHeader);
    }
    
    // Create expert cards
    const row = document.createElement('div');
    row.className = 'row';
    
    experts.forEach(expert => {
        const col = document.createElement('div');
        col.className = 'col-md-6 mb-3';
        
        // Show "View All" link for experts with multiple comments
        const viewAllLink = expert.comment_count > 1 ? 
            `<a href="#" class="text-primary small" onclick="viewExpertHistory('${expert.id}'); return false;">
                <i class="fas fa-history me-1"></i>View all ${expert.comment_count} comments
            </a>` : '';
        
        // Display expertise badges
        const expertiseBadges = expert.expertise ? 
            expert.expertise.map(skill => `<span class="badge bg-secondary me-1" style="font-size: 0.7rem;">${skill}</span>`).join('') : '';
        
        col.innerHTML = `
            <div class="commentary-card p-3 border border-secondary rounded" style="cursor: pointer;" onclick="viewExpertProfile('${expert.id}')">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="d-flex align-items-center">
                        <div class="avatar bg-${expert.avatar_color || 'primary'} rounded-circle p-2 me-2">
                            <i class="fas fa-user text-white"></i>
                        </div>
                        <div>
                            <h6 class="text-white mb-0">${expert.name}</h6>
                            <small class="text-muted">${expert.title}</small><br>
                            <small class="text-info">${expert.organization}</small>
                        </div>
                    </div>
                    ${expert.comment_count > 1 ? `<span class="badge bg-warning">${expert.comment_count} posts</span>` : ''}
                </div>
                ${expertiseBadges ? `<div class="mb-2">${expertiseBadges}</div>` : ''}
                <p class="text-white small mb-2" style="line-height: 1.6;">
                    "${expert.latest_comment.text}"
                </p>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>${expert.latest_comment.time}
                        ${expert.latest_comment.likes ? `<span class="ms-2"><i class="fas fa-thumbs-up me-1"></i>${expert.latest_comment.likes}</span>` : ''}
                    </small>
                    ${viewAllLink}
                </div>
            </div>
        `;
        
        row.appendChild(col);
    });
    
    container.appendChild(row);
    
    // Add frequent contributors section if any
    if (frequentExperts && frequentExperts.length > 0) {
        const frequentSection = document.createElement('div');
        frequentSection.className = 'mt-3 p-3 border border-info rounded';
        frequentSection.innerHTML = `
            <h6 class="text-info mb-2">
                <i class="fas fa-star me-2"></i>Top Contributors
            </h6>
            <div class="d-flex flex-wrap gap-2">
                ${frequentExperts.slice(0, 6).map(expert => `
                    <button class="btn btn-sm btn-outline-info" onclick="viewExpertHistory('${expert.id}')">
                        ${expert.name} (${expert.comment_count} posts)
                    </button>
                `).join('')}
            </div>
        `;
        container.appendChild(frequentSection);
    }
}

// Navigate commentary pages
function navigateCommentary(direction) {
    if (direction === 'prev' && currentCommentaryPage > 0) {
        loadMarketCommentary(currentCommentaryPage - 1);
    } else if (direction === 'next') {
        loadMarketCommentary(currentCommentaryPage + 1);
    }
}

// View expert history
async function viewExpertHistory(expertId) {
    try {
        const response = await fetch(`/api/expert-history/${expertId}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            showExpertHistoryModal(data.expert);
        }
    } catch (error) {
        console.error('Error loading expert history:', error);
    }
}

// Show expert history modal
function showExpertHistoryModal(expert) {
    // Remove any existing modal and backdrop
    const existingModal = document.getElementById('expertHistoryModal');
    if (existingModal) {
        const modalInstance = bootstrap.Modal.getInstance(existingModal);
        if (modalInstance) {
            modalInstance.dispose();
        }
        existingModal.remove();
    }
    
    // Remove any lingering modal backdrops
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('padding-right');
    
    // Create modal HTML
    const modalHTML = `
        <div class="modal fade" id="expertHistoryModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
                <div class="modal-content" style="background: rgba(31, 41, 55, 0.98); border: 1px solid #60a5fa;">
                    <div class="modal-header border-bottom border-secondary">
                        <div class="d-flex align-items-center w-100">
                            <div class="avatar bg-${expert.avatar_color || 'primary'} rounded-circle p-2 me-3">
                                <i class="fas fa-user text-white fa-lg"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h5 class="modal-title text-white mb-0">${expert.name}</h5>
                                <small class="text-muted">${expert.title} at ${expert.organization}</small>
                            </div>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                    </div>
                    <div class="modal-body">
                        <!-- Expert Info -->
                        <div class="mb-3 p-3 bg-dark rounded">
                            <div class="row">
                                <div class="col-md-6">
                                    <small class="text-muted d-block mb-1">Areas of Expertise</small>
                                    <div>
                                        ${expert.expertise.map(skill => `<span class="badge bg-primary me-1">${skill}</span>`).join('')}
                                    </div>
                                </div>
                                <div class="col-md-6 text-md-end">
                                    <small class="text-muted d-block mb-1">Activity</small>
                                    <span class="text-white">${expert.comment_count} Total Comments</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Comments Timeline -->
                        <h6 class="text-white mb-3">
                            <i class="fas fa-comments me-2"></i>Recent Commentary
                        </h6>
                        <div class="comments-timeline">
                            ${expert.comments.map((comment, index) => `
                                <div class="comment-item mb-3 pb-3 ${index < expert.comments.length - 1 ? 'border-bottom border-secondary' : ''}">
                                    <div class="d-flex justify-content-between align-items-start mb-2">
                                        <span class="badge bg-info">${comment.topic}</span>
                                        <small class="text-muted">${comment.time}</small>
                                    </div>
                                    <p class="text-white mb-2" style="line-height: 1.7;">
                                        ${comment.text}
                                    </p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <button class="btn btn-sm btn-outline-success me-2" onclick="likeComment('${expert.id}', ${index})">
                                                <i class="fas fa-thumbs-up me-1"></i>${comment.likes || 0}
                                            </button>
                                            <button class="btn btn-sm btn-outline-primary" onclick="shareComment('${expert.id}', ${index})">
                                                <i class="fas fa-share me-1"></i>Share
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="modal-footer border-top border-secondary">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="followExpert('${expert.id}')">
                            <i class="fas fa-user-plus me-1"></i>Follow ${expert.name}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Initialize and show modal
    const modalElement = document.getElementById('expertHistoryModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Clean up modal after it's hidden
    modalElement.addEventListener('hidden.bs.modal', function() {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.dispose();
        }
        modalElement.remove();
        // Extra cleanup for any lingering backdrops
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('padding-right');
    });
}

// View expert profile (simplified view)
function viewExpertProfile(expertId) {
    // Find expert in current data
    const expert = commentaryExperts.find(e => e.id === expertId) || 
                   frequentExperts.find(e => e.id === expertId);
    
    if (expert && expert.comment_count > 1) {
        viewExpertHistory(expertId);
    }
}

// Like a comment
function likeComment(expertId, commentIndex) {
    // Placeholder for like functionality
    showToast('Comment liked!', 'success');
}

// Share a comment
function shareComment(expertId, commentIndex) {
    // Placeholder for share functionality
    const shareUrl = `${window.location.origin}/expert/${expertId}/comment/${commentIndex}`;
    navigator.clipboard.writeText(shareUrl).then(() => {
        showToast('Comment link copied to clipboard!', 'success');
    });
}

// Follow an expert
function followExpert(expertId) {
    // Placeholder for follow functionality
    const followedExperts = JSON.parse(localStorage.getItem('followedExperts') || '[]');
    if (!followedExperts.includes(expertId)) {
        followedExperts.push(expertId);
        localStorage.setItem('followedExperts', JSON.stringify(followedExperts));
        showToast('You are now following this expert!', 'success');
    } else {
        showToast('You are already following this expert', 'info');
    }
}

// Update sentiment gauge
function updateSentimentGauge(sentiment, score) {
    const gauge = document.getElementById('sentimentGauge');
    if (!gauge) return;
    
    const colors = {
        'BULLISH': 'success',
        'NEUTRAL': 'warning',
        'BEARISH': 'danger'
    };
    
    const color = colors[sentiment] || 'secondary';
    gauge.innerHTML = `<span class="badge bg-${color} fs-5">${sentiment}</span>`;
}

// Update market metrics
function updateMarketMetrics(data) {
    const issuanceElement = document.getElementById('issuanceVolume');
    const activeDealsElement = document.getElementById('activeDeals');
    const spreadChangeElement = document.getElementById('avgSpreadChange');
    
    if (issuanceElement) {
        const trendIcon = data.issuance_trend === 'up' ? '↑' : data.issuance_trend === 'down' ? '↓' : '→';
        const trendClass = data.issuance_trend === 'up' ? 'text-success' : data.issuance_trend === 'down' ? 'text-danger' : 'text-warning';
        issuanceElement.innerHTML = `<h4 class="${trendClass}">${data.issuance_24h} <i class="fas fa-arrow-${data.issuance_trend}"></i></h4>`;
    }
    
    if (activeDealsElement) {
        activeDealsElement.innerHTML = `<h4 class="text-white">${data.active_deals}</h4>`;
    }
    
    if (spreadChangeElement) {
        const changeClass = data.avg_spread_change > 0 ? 'text-danger' : 'text-success';
        const changeIcon = data.avg_spread_change > 0 ? 'up' : 'down';
        spreadChangeElement.innerHTML = `<h4 class="${changeClass}">${data.avg_spread_change > 0 ? '+' : ''}${data.avg_spread_change} bps <i class="fas fa-arrow-${changeIcon}"></i></h4>`;
    }
}

// Update indicators
function updateIndicators(indicators) {
    Object.keys(indicators).forEach(key => {
        const indicator = indicators[key];
        updateIndicator(key, indicator);
    });
}

// Update single indicator
function updateIndicator(key, data) {
    const element = document.querySelector(`[data-indicator="${key}"]`);
    if (!element) return;
    
    const changeIcon = data.change === 'up' ? '↑' : data.change === 'down' ? '↓' : '→';
    const changeClass = data.change === 'up' ? 'text-success' : data.change === 'down' ? 'text-danger' : 'text-warning';
    
    element.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="text-white">${key.replace('_', ' ')}</span>
            <span class="${changeClass}">${data.value} ${changeIcon}</span>
        </div>
        <div class="progress" style="height: 6px;">
            <div class="progress-bar bg-${data.change === 'up' ? 'success' : data.change === 'down' ? 'danger' : 'warning'}" style="width: ${data.progress}%"></div>
        </div>
    `;
}

// Setup event listeners
function setupEventListeners() {
    // Region filter
    const regionFilter = document.getElementById('regionFilter');
    if (regionFilter) {
        regionFilter.addEventListener('change', applyFilters);
    }
    
    // Asset filter
    const assetFilter = document.getElementById('assetFilter');
    if (assetFilter) {
        assetFilter.addEventListener('change', applyFilters);
    }
    
    // Source filter
    const sourceFilter = document.getElementById('sourceFilter');
    if (sourceFilter) {
        sourceFilter.addEventListener('change', applyFilters);
    }
    
    // Search input
    const searchInput = document.getElementById('newsSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', debounce(applyFilters, 500));
    }
    
    // Search button
    const searchBtn = document.querySelector('[onclick="searchNews()"]');
    if (searchBtn) {
        searchBtn.addEventListener('click', applyFilters);
    }
}

// Apply filters
function applyFilters() {
    const filters = {
        region: document.getElementById('regionFilter')?.value || 'all',
        asset: document.getElementById('assetFilter')?.value || 'all',
        source: document.getElementById('sourceFilter')?.value || 'all',
        search: document.getElementById('newsSearch')?.value || ''
    };
    
    loadMarketNews(filters);
}

// Search news
function searchNews(query) {
    const searchInput = document.getElementById('newsSearch');
    if (searchInput) {
        searchInput.value = query;
        applyFilters();
    }
}

// Load more news
function loadMoreNews() {
    // In a real implementation, this would load additional news items
    // For now, we'll just reload with a larger limit
    const filters = {
        region: document.getElementById('regionFilter')?.value || 'all',
        asset: document.getElementById('assetFilter')?.value || 'all',
        source: document.getElementById('sourceFilter')?.value || 'all',
        search: document.getElementById('newsSearch')?.value || '',
        limit: currentNewsData.length + 20
    };
    
    loadMarketNews(filters);
}

// Open news detail
function openNewsDetail(item) {
    // Remove any existing modal and backdrop
    const existingModal = document.getElementById('newsDetailModal');
    if (existingModal) {
        const modalInstance = bootstrap.Modal.getInstance(existingModal);
        if (modalInstance) {
            modalInstance.dispose();
        }
        existingModal.remove();
    }
    
    // Remove any lingering modal backdrops
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('padding-right');
    
    // Determine badge color and icons
    const badgeColors = {
        'BREAKING': 'danger',
        'MARKET MOVE': 'primary',
        'ANALYSIS': 'warning',
        'DEAL NEWS': 'success',
        'REGULATORY': 'info'
    };
    
    const sentimentColors = {
        'positive': 'success',
        'neutral': 'warning',
        'negative': 'danger'
    };
    
    const impactColors = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'info'
    };
    
    const badgeColor = badgeColors[item.type] || 'secondary';
    const sentimentColor = sentimentColors[item.sentiment] || 'secondary';
    const impactColor = impactColors[item.impact] || 'secondary';
    
    // Create modal HTML
    const modalHTML = `
        <div class="modal fade" id="newsDetailModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content" style="background: rgba(31, 41, 55, 0.98); border: 1px solid #60a5fa;">
                    <div class="modal-header border-bottom border-secondary">
                        <div class="d-flex align-items-center w-100">
                            <span class="badge bg-${badgeColor} me-2">${item.type}</span>
                            <h5 class="modal-title text-white flex-grow-1">${item.title}</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                    </div>
                    <div class="modal-body">
                        <!-- Article Meta Info -->
                        <div class="row mb-3">
                            <div class="col-md-4">
                                <small class="text-muted">Source</small>
                                <p class="text-white mb-2">
                                    <i class="fas fa-newspaper me-1"></i>${item.source}
                                </p>
                            </div>
                            <div class="col-md-4">
                                <small class="text-muted">Published</small>
                                <p class="text-white mb-2">
                                    <i class="fas fa-clock me-1"></i>${item.time}
                                </p>
                            </div>
                            <div class="col-md-4">
                                <small class="text-muted">Region</small>
                                <p class="text-white mb-2">
                                    <i class="fas fa-globe me-1"></i>${item.region}
                                </p>
                            </div>
                        </div>
                        
                        <!-- Article Content -->
                        <div class="article-content border-top border-bottom border-secondary py-3 mb-3">
                            <p class="text-white" style="line-height: 1.8; font-size: 1.05rem;">
                                ${item.content}
                            </p>
                            
                            <!-- Extended content placeholder -->
                            <p class="text-muted mt-3">
                                <em>This article continues with detailed analysis of the ${item.asset_class} market in ${item.region}, 
                                examining recent trends, regulatory impacts, and forward-looking projections. 
                                Market participants should monitor these developments closely as they may impact pricing 
                                and issuance strategies in the coming quarters.</em>
                            </p>
                        </div>
                        
                        <!-- Article Metadata -->
                        <div class="row">
                            <div class="col-md-6">
                                <small class="text-muted d-block mb-2">Asset Class</small>
                                <span class="badge bg-primary me-2">${item.asset_class}</span>
                            </div>
                            <div class="col-md-3">
                                <small class="text-muted d-block mb-2">Market Impact</small>
                                <span class="badge bg-${impactColor}">${item.impact.toUpperCase()}</span>
                            </div>
                            <div class="col-md-3">
                                <small class="text-muted d-block mb-2">Sentiment</small>
                                <span class="badge bg-${sentimentColor}">${item.sentiment.toUpperCase()}</span>
                            </div>
                        </div>
                        
                        <!-- Tags -->
                        <div class="mt-3">
                            <small class="text-muted d-block mb-2">Related Topics</small>
                            <div>
                                ${item.tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('')}
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer border-top border-secondary">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        ${item.external_url ? `
                        <a href="${item.external_url}" target="_blank" class="btn btn-info">
                            <i class="fas fa-external-link-alt me-1"></i>Read on ${item.source}
                        </a>` : ''}
                        <button type="button" class="btn btn-primary" onclick="shareArticle('${item.id}')">
                            <i class="fas fa-share-alt me-1"></i>Share
                        </button>
                        <button type="button" class="btn btn-success" onclick="saveArticle('${item.id}')">
                            <i class="fas fa-bookmark me-1"></i>Save for Later
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Initialize and show modal
    const modalElement = document.getElementById('newsDetailModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Clean up modal after it's hidden
    modalElement.addEventListener('hidden.bs.modal', function() {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.dispose();
        }
        modalElement.remove();
        // Extra cleanup for any lingering backdrops
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('padding-right');
    });
}

// Share article function
function shareArticle(articleId) {
    // Placeholder for share functionality
    const shareUrl = `${window.location.origin}/market/article/${articleId}`;
    if (navigator.share) {
        navigator.share({
            title: 'Securitisation Market Update',
            text: 'Check out this market update from Atlas Nexus',
            url: shareUrl
        }).catch(err => console.log('Error sharing:', err));
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareUrl).then(() => {
            showToast('Link copied to clipboard!', 'success');
        });
    }
}

// Save article function - now saves to user account
async function saveArticle(articleId) {
    // Find the article in current news data
    const article = currentNewsData.find(item => item.id === articleId);
    if (!article) {
        showToast('Article not found', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/saved-articles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(article)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('Article saved successfully!', 'success');
            updateSavedArticleCount();
        } else if (data.status === 'info') {
            showToast(data.message, 'info');
        } else {
            showToast('Error saving article', 'error');
        }
    } catch (error) {
        console.error('Error saving article:', error);
        showToast('Error saving article', 'error');
    }
}

// Load saved articles count
async function updateSavedArticleCount() {
    try {
        const response = await fetch('/api/saved-articles');
        const data = await response.json();
        
        if (data.status === 'success') {
            const countElement = document.getElementById('savedArticleCount');
            if (countElement) {
                countElement.textContent = data.count;
            }
        }
    } catch (error) {
        console.error('Error loading saved articles count:', error);
    }
}

// Show saved articles modal
async function showSavedArticles() {
    try {
        const response = await fetch('/api/saved-articles');
        const data = await response.json();
        
        if (data.status === 'success') {
            showSavedArticlesModal(data.articles);
        }
    } catch (error) {
        console.error('Error loading saved articles:', error);
        showToast('Error loading saved articles', 'error');
    }
}

// Display saved articles modal
function showSavedArticlesModal(articles) {
    // Remove any existing modal and backdrop
    const existingModal = document.getElementById('savedArticlesModal');
    if (existingModal) {
        const modalInstance = bootstrap.Modal.getInstance(existingModal);
        if (modalInstance) {
            modalInstance.dispose();
        }
        existingModal.remove();
    }
    
    // Remove any lingering modal backdrops
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('padding-right');
    
    // Create modal HTML
    const modalHTML = `
        <div class="modal fade" id="savedArticlesModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
                <div class="modal-content" style="background: rgba(31, 41, 55, 0.98); border: 1px solid #60a5fa;">
                    <div class="modal-header border-bottom border-secondary">
                        <h5 class="modal-title text-white">
                            <i class="fas fa-bookmark me-2"></i>Saved Articles (${articles.length})
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${articles.length === 0 ? 
                            '<p class="text-muted text-center py-4">No saved articles yet. Click "Save for Later" on any article to save it here.</p>' :
                            `<div class="saved-articles-list">
                                ${articles.map(article => `
                                    <div class="saved-article-item border-bottom border-secondary pb-3 mb-3" data-article-id="${article.id}">
                                        <div class="d-flex justify-content-between align-items-start mb-2">
                                            <span class="badge bg-${getBadgeColor(article.type)}">${article.type}</span>
                                            <div>
                                                <small class="text-muted me-2">Saved ${getTimeAgo(article.saved_at)}</small>
                                                <button class="btn btn-sm btn-outline-danger" onclick="removeSavedArticle('${article.id}')">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </div>
                                        </div>
                                        <h6 class="text-white mb-2" style="cursor: pointer;" onclick='openSavedNewsDetail(${JSON.stringify(article).replace(/'/g, "&apos;")})'>${article.title}</h6>
                                        <p class="text-muted small mb-2">${article.content ? article.content.substring(0, 150) + '...' : ''}</p>
                                        <div class="d-flex justify-content-between align-items-center">
                                            <small class="text-info">
                                                <i class="fas fa-tag me-1"></i>${article.tags ? article.tags.slice(0, 3).join(' • ') : ''}
                                            </small>
                                            <small class="text-warning">
                                                <i class="fas fa-newspaper me-1"></i>${article.source}
                                            </small>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>`
                        }
                    </div>
                    <div class="modal-footer border-top border-secondary">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        ${articles.length > 0 ? 
                            '<button type="button" class="btn btn-danger" onclick="clearAllSavedArticles()"><i class="fas fa-trash-alt me-1"></i>Clear All</button>' : ''
                        }
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Initialize and show modal
    const modalElement = document.getElementById('savedArticlesModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Clean up modal after it's hidden
    modalElement.addEventListener('hidden.bs.modal', function() {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.dispose();
        }
        modalElement.remove();
        // Extra cleanup for any lingering backdrops
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('padding-right');
    });
}

// Remove saved article
async function removeSavedArticle(articleId) {
    try {
        const response = await fetch(`/api/saved-articles?article_id=${articleId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Remove from modal
            const articleElement = document.querySelector(`[data-article-id="${articleId}"]`);
            if (articleElement) {
                articleElement.remove();
            }
            
            // Update count
            updateSavedArticleCount();
            showToast('Article removed', 'success');
            
            // Update modal title count
            const modalTitle = document.querySelector('#savedArticlesModal .modal-title');
            if (modalTitle) {
                modalTitle.innerHTML = `<i class="fas fa-bookmark me-2"></i>Saved Articles (${data.count})`;
            }
        }
    } catch (error) {
        console.error('Error removing saved article:', error);
        showToast('Error removing article', 'error');
    }
}

// Clear all saved articles
async function clearAllSavedArticles() {
    if (!confirm('Are you sure you want to clear all saved articles?')) {
        return;
    }
    
    try {
        // Get all saved articles first
        const response = await fetch('/api/saved-articles');
        const data = await response.json();
        
        if (data.status === 'success' && data.articles.length > 0) {
            // Remove each article
            for (const article of data.articles) {
                await fetch(`/api/saved-articles?article_id=${article.id}`, {
                    method: 'DELETE'
                });
            }
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('savedArticlesModal'));
            if (modal) {
                modal.hide();
            }
            
            updateSavedArticleCount();
            showToast('All saved articles cleared', 'success');
        }
    } catch (error) {
        console.error('Error clearing saved articles:', error);
        showToast('Error clearing articles', 'error');
    }
}

// Open saved news detail (reuse existing modal)
function openSavedNewsDetail(article) {
    openNewsDetail(article);
}

// Get badge color helper
function getBadgeColor(type) {
    const colors = {
        'BREAKING': 'danger',
        'MARKET MOVE': 'primary',
        'ANALYSIS': 'warning',
        'DEAL NEWS': 'success',
        'REGULATORY': 'info'
    };
    return colors[type] || 'secondary';
}

// Get time ago helper
function getTimeAgo(timestamp) {
    if (!timestamp) return 'recently';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    if (days < 30) return `${days} day${days !== 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
}

// Show active deals modal
async function showActiveDeals() {
    try {
        const response = await fetch('/api/active-deals');
        const data = await response.json();
        
        if (data.status === 'success') {
            showActiveDealsModal(data.deals, data.summary);
        }
    } catch (error) {
        console.error('Error loading active deals:', error);
        showToast('Error loading active deals', 'error');
    }
}

// Display active deals modal
function showActiveDealsModal(deals, summary) {
    // Remove any existing modal and backdrop
    const existingModal = document.getElementById('activeDealsModal');
    if (existingModal) {
        const modalInstance = bootstrap.Modal.getInstance(existingModal);
        if (modalInstance) {
            modalInstance.dispose();
        }
        existingModal.remove();
    }
    
    // Remove any lingering modal backdrops
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('padding-right');
    
    // Format currency
    function formatCurrency(amount, currency = 'EUR') {
        const symbols = { 'EUR': '€', 'USD': '$', 'GBP': '£' };
        const symbol = symbols[currency] || currency;
        if (amount >= 1000000000) {
            return `${symbol}${(amount / 1000000000).toFixed(1)}B`;
        } else if (amount >= 1000000) {
            return `${symbol}${(amount / 1000000).toFixed(0)}M`;
        }
        return `${symbol}${amount.toLocaleString()}`;
    }
    
    // Create modal HTML
    const modalHTML = `
        <div class="modal fade" id="activeDealsModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
                <div class="modal-content" style="background: rgba(31, 41, 55, 0.98); border: 1px solid #60a5fa; max-height: 90vh;">
                    <div class="modal-header border-bottom border-secondary">
                        <h5 class="modal-title text-white">
                            <i class="fas fa-handshake me-2"></i>Active Securitization Deals (${deals.length})
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Summary Statistics -->
                        <div class="row mb-4">
                            <div class="col-md-3">
                                <div class="stat-box text-center p-2 border border-secondary rounded">
                                    <small class="text-muted">Total Volume</small>
                                    <h5 class="text-warning">${formatCurrency(summary.total_volume)}</h5>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="stat-box text-center p-2 border border-secondary rounded">
                                    <small class="text-muted">Active Deals</small>
                                    <h5 class="text-info">${summary.total_deals}</h5>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="stat-box text-center p-2 border border-secondary rounded">
                                    <small class="text-muted">Avg Deal Size</small>
                                    <h5 class="text-success">${formatCurrency(summary.total_volume / summary.total_deals)}</h5>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="stat-box text-center p-2 border border-secondary rounded">
                                    <small class="text-muted">In Marketing</small>
                                    <h5 class="text-primary">${summary.by_status['Marketing'] || 0}</h5>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Deals Table -->
                        <div class="table-responsive">
                            <table class="table table-dark table-hover">
                                <thead>
                                    <tr>
                                        <th>Deal Name</th>
                                        <th>Asset Class</th>
                                        <th>Region</th>
                                        <th>Size</th>
                                        <th>Status</th>
                                        <th>Lead Manager</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${deals.map(deal => `
                                        <tr>
                                            <td class="text-white fw-bold">${deal.name}</td>
                                            <td><span class="badge bg-primary">${deal.asset_class}</span></td>
                                            <td>${deal.region}</td>
                                            <td class="text-warning">${formatCurrency(deal.total_size, deal.currency)}</td>
                                            <td><span class="badge bg-${deal.status_color || 'secondary'}">${deal.status}</span></td>
                                            <td>${deal.lead_manager}</td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-info" onclick='viewDealDetails(${JSON.stringify(deal).replace(/'/g, "&apos;")})'>
                                                    <i class="fas fa-eye"></i> Details
                                                </button>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- Asset Class Distribution -->
                        <div class="row mt-4">
                            <div class="col-md-6">
                                <h6 class="text-white mb-3">By Asset Class</h6>
                                <div class="asset-distribution">
                                    ${Object.entries(summary.by_asset_class).map(([asset, data]) => `
                                        <div class="d-flex justify-content-between mb-2 pb-2 border-bottom border-secondary">
                                            <span class="text-white">${asset}</span>
                                            <span class="text-muted">${data.count} deals / ${formatCurrency(data.volume)}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6 class="text-white mb-3">By Region</h6>
                                <div class="region-distribution">
                                    ${Object.entries(summary.by_region).map(([region, data]) => `
                                        <div class="d-flex justify-content-between mb-2 pb-2 border-bottom border-secondary">
                                            <span class="text-white">${region}</span>
                                            <span class="text-muted">${data.count} deals / ${formatCurrency(data.volume)}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer border-top border-secondary">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="exportDeals()">
                            <i class="fas fa-download me-1"></i>Export to Excel
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Initialize and show modal
    const modalElement = document.getElementById('activeDealsModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Clean up modal after it's hidden
    modalElement.addEventListener('hidden.bs.modal', function() {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.dispose();
        }
        modalElement.remove();
        // Extra cleanup for any lingering backdrops
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('padding-right');
    });
}

// View individual deal details
function viewDealDetails(deal) {
    // Close the active deals modal first
    const activeDealsModal = bootstrap.Modal.getInstance(document.getElementById('activeDealsModal'));
    if (activeDealsModal) {
        activeDealsModal.hide();
    }
    
    // Format currency helper
    function formatCurrency(amount, currency = 'EUR') {
        const symbols = { 'EUR': '€', 'USD': '$', 'GBP': '£' };
        const symbol = symbols[currency] || currency;
        if (amount >= 1000000000) {
            return `${symbol}${(amount / 1000000000).toFixed(2)}B`;
        } else if (amount >= 1000000) {
            return `${symbol}${(amount / 1000000).toFixed(0)}M`;
        }
        return `${symbol}${amount.toLocaleString()}`;
    }
    
    // Create detailed view modal
    const detailHTML = `
        <div class="modal fade" id="dealDetailModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
                <div class="modal-content" style="background: rgba(31, 41, 55, 0.98); border: 1px solid #60a5fa;">
                    <div class="modal-header border-bottom border-secondary">
                        <div class="w-100">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h4 class="modal-title text-white mb-1">${deal.name}</h4>
                                    <small class="text-muted">${deal.issuer}</small>
                                </div>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                        </div>
                    </div>
                    <div class="modal-body">
                        <!-- Deal Overview -->
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <h6 class="text-info mb-3">Deal Structure</h6>
                                <table class="table table-sm table-dark">
                                    <tr><td class="text-muted">Asset Class:</td><td class="text-white">${deal.asset_class}</td></tr>
                                    <tr><td class="text-muted">Total Size:</td><td class="text-warning">${formatCurrency(deal.total_size, deal.currency)}</td></tr>
                                    <tr><td class="text-muted">Currency:</td><td class="text-white">${deal.currency}</td></tr>
                                    <tr><td class="text-muted">Status:</td><td><span class="badge bg-${deal.status_color}">${deal.status}</span></td></tr>
                                    <tr><td class="text-muted">Pricing Date:</td><td class="text-white">${new Date(deal.pricing_date).toLocaleDateString()}</td></tr>
                                    <tr><td class="text-muted">Closing Date:</td><td class="text-white">${new Date(deal.closing_date).toLocaleDateString()}</td></tr>
                                    <tr><td class="text-muted">Legal Structure:</td><td class="text-white">${deal.legal_structure}</td></tr>
                                    <tr><td class="text-muted">Listing:</td><td class="text-white">${deal.listing || 'N/A'}</td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h6 class="text-info mb-3">Parties</h6>
                                <table class="table table-sm table-dark">
                                    <tr><td class="text-muted">Lead Manager:</td><td class="text-white">${deal.lead_manager}</td></tr>
                                    <tr><td class="text-muted">Co-Managers:</td><td class="text-white">${deal.co_managers ? deal.co_managers.join(', ') : 'N/A'}</td></tr>
                                    <tr><td class="text-muted">Originator:</td><td class="text-white">${deal.originator}</td></tr>
                                    <tr><td class="text-muted">Servicer:</td><td class="text-white">${deal.servicer || deal.special_servicer || 'N/A'}</td></tr>
                                    <tr><td class="text-muted">Region:</td><td class="text-white">${deal.region}</td></tr>
                                    <tr><td class="text-muted">Subscription:</td><td class="text-success">${deal.subscription_level}</td></tr>
                                </table>
                            </div>
                        </div>
                        
                        <!-- Tranches -->
                        <h6 class="text-info mb-3">Tranche Structure</h6>
                        <div class="table-responsive mb-4">
                            <table class="table table-dark table-sm">
                                <thead>
                                    <tr>
                                        <th>Class</th>
                                        <th>Size</th>
                                        <th>Rating</th>
                                        <th>Coupon</th>
                                        <th>WAL</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${deal.tranches.map(tranche => `
                                        <tr>
                                            <td class="text-white">Class ${tranche.class}</td>
                                            <td class="text-warning">${formatCurrency(tranche.size, deal.currency)}</td>
                                            <td><span class="badge bg-${tranche.rating === 'AAA' ? 'success' : tranche.rating === 'AA' ? 'info' : 'warning'}">${tranche.rating}</span></td>
                                            <td class="text-white">${tranche.coupon}</td>
                                            <td class="text-muted">${tranche.wal}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- Collateral Information -->
                        <h6 class="text-info mb-3">Collateral & Pool Characteristics</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="p-3 border border-secondary rounded mb-3">
                                    <p class="text-white mb-2"><strong>Collateral Type:</strong></p>
                                    <p class="text-muted">${deal.collateral}</p>
                                    ${deal.pool_characteristics ? `
                                        <ul class="list-unstyled text-muted small">
                                            ${Object.entries(deal.pool_characteristics).map(([key, value]) => `
                                                <li><span class="text-white">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span> ${value}</li>
                                            `).join('')}
                                        </ul>
                                    ` : ''}
                                </div>
                            </div>
                            <div class="col-md-6">
                                ${deal.performance ? `
                                    <div class="p-3 border border-success rounded mb-3">
                                        <h6 class="text-success mb-2">Performance Metrics</h6>
                                        <ul class="list-unstyled text-muted small mb-0">
                                            <li>Spread Tightening: <span class="text-success">${deal.performance.spread_tightening}bps</span></li>
                                            <li>Final Allocation: ${deal.performance.final_allocation}</li>
                                            <li>Geographic Distribution: ${deal.performance.geographic_distribution}</li>
                                        </ul>
                                    </div>
                                ` : ''}
                                ${deal.guarantee ? `
                                    <div class="alert alert-info">
                                        <i class="fas fa-shield-alt me-2"></i>${deal.guarantee}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer border-top border-secondary">
                        <button type="button" class="btn btn-secondary" onclick="backToDeals()">
                            <i class="fas fa-arrow-left me-1"></i>Back to Deals
                        </button>
                        <button type="button" class="btn btn-primary" onclick="shareDeal('${deal.id}')">
                            <i class="fas fa-share me-1"></i>Share Deal
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing detail modal if any
    const existingDetail = document.getElementById('dealDetailModal');
    if (existingDetail) {
        existingDetail.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', detailHTML);
    
    // Show the detail modal
    const detailModal = new bootstrap.Modal(document.getElementById('dealDetailModal'));
    detailModal.show();
    
    // Clean up on close
    document.getElementById('dealDetailModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('padding-right');
    });
}

// Back to deals list
function backToDeals() {
    const detailModal = bootstrap.Modal.getInstance(document.getElementById('dealDetailModal'));
    if (detailModal) {
        detailModal.hide();
    }
    showActiveDeals();
}

// Export deals to Excel (placeholder)
function exportDeals() {
    showToast('Export functionality coming soon!', 'info');
}

// Share deal (placeholder)
function shareDeal(dealId) {
    const shareUrl = `${window.location.origin}/deal/${dealId}`;
    navigator.clipboard.writeText(shareUrl).then(() => {
        showToast('Deal link copied to clipboard!', 'success');
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastHTML = `
        <div class="toast position-fixed bottom-0 end-0 m-3" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} text-white">
                <strong class="me-auto">Atlas Nexus</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.querySelector('.toast:last-child');
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Start auto refresh
function startAutoRefresh() {
    // Refresh every 30 seconds
    updateInterval = setInterval(() => {
        loadMarketIndicators();
        loadMarketNews();
        updateLastRefreshTime();
    }, 30000);
}

// Stop auto refresh
function stopAutoRefresh() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

// Update last refresh time
function updateLastRefreshTime() {
    const element = document.getElementById('lastUpdateTime');
    if (element) {
        element.textContent = 'Just now';
        
        // Update the time every minute
        setTimeout(() => {
            if (element) {
                element.textContent = '1 minute ago';
            }
        }, 60000);
    }
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.marketNews = {
    initialize: initializeMarketNews,
    loadNews: loadMarketNews,
    searchNews: searchNews,
    loadMoreNews: loadMoreNews,
    refresh: () => {
        loadMarketIndicators();
        loadMarketNews();
        loadRegionalData();
        loadTrendingTopics();
        loadMarketEvents();
        loadMarketCommentary();
        updateLastRefreshTime();
    }
};