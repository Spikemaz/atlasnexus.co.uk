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

// Load market commentary
async function loadMarketCommentary() {
    try {
        const response = await fetch('/api/market-commentary');
        const data = await response.json();
        
        if (data.status === 'success') {
            renderMarketCommentary(data.commentary);
        }
    } catch (error) {
        console.error('Error loading market commentary:', error);
    }
}

// Render market commentary
function renderMarketCommentary(commentary) {
    const container = document.querySelector('.commentary-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    const row = document.createElement('div');
    row.className = 'row';
    
    commentary.forEach(comment => {
        const col = document.createElement('div');
        col.className = 'col-md-6 mb-3';
        
        const avatarColors = ['primary', 'success', 'warning', 'info'];
        const avatarColor = avatarColors[Math.floor(Math.random() * avatarColors.length)];
        
        col.innerHTML = `
            <div class="commentary-card p-3 border border-secondary rounded">
                <div class="d-flex align-items-center mb-2">
                    <div class="avatar bg-${avatarColor} rounded-circle p-2 me-2">
                        <i class="fas fa-user text-white"></i>
                    </div>
                    <div>
                        <h6 class="text-white mb-0">${comment.name}</h6>
                        <small class="text-muted">${comment.title}, ${comment.organization}</small>
                    </div>
                </div>
                <p class="text-muted small mb-0">"${comment.comment}"</p>
                <small class="text-info">${comment.time}</small>
            </div>
        `;
        
        row.appendChild(col);
    });
    
    container.appendChild(row);
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
    // Remove any existing modal
    const existingModal = document.getElementById('newsDetailModal');
    if (existingModal) {
        existingModal.remove();
    }
    
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
        modalElement.remove();
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

// Save article function
function saveArticle(articleId) {
    // Placeholder for save functionality
    const savedArticles = JSON.parse(localStorage.getItem('savedArticles') || '[]');
    if (!savedArticles.includes(articleId)) {
        savedArticles.push(articleId);
        localStorage.setItem('savedArticles', JSON.stringify(savedArticles));
        showToast('Article saved successfully!', 'success');
    } else {
        showToast('Article already saved', 'info');
    }
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