class CommunityAggregator {
    constructor() {
        this.posts = [];
        this.filteredPosts = [];
        this.currentPage = 1;
        this.postsPerPage = 20;
        this.currentFilters = {
            site: 'all',
            sort: 'latest',
            search: ''
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadPosts();
        this.loadStats();
    }
    
    bindEvents() {
        // 필터 이벤트
        document.getElementById('siteFilter').addEventListener('change', (e) => {
            this.currentFilters.site = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById('sortFilter').addEventListener('change', (e) => {
            this.currentFilters.sort = e.target.value;
            this.applyFilters();
        });
        
        // 검색 이벤트
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.currentFilters.search = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById('searchBtn').addEventListener('click', () => {
            this.applyFilters();
        });
        
        // 새로고침 이벤트
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshData();
        });
        
        // 더 보기 이벤트
        document.getElementById('loadMoreBtn').addEventListener('click', () => {
            this.loadMorePosts();
        });
        
        // 엔터키 검색
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.applyFilters();
            }
        });
    }
    
    async loadPosts() {
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/posts?limit=100');
            const data = await response.json();
            
            this.posts = data.posts;
            this.applyFilters();
            this.updateLastUpdate();
            
        } catch (error) {
            console.error('게시물 로딩 오류:', error);
            this.showError('게시물을 불러오는데 실패했습니다.');
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            document.getElementById('totalPosts').textContent = data.total_posts;
            
        } catch (error) {
            console.error('통계 로딩 오류:', error);
        }
    }
    
    async refreshData() {
        try {
            this.showLoading(true);
            
            // 수동 크롤링 실행
            const crawlResponse = await fetch('/api/crawl');
            const crawlData = await crawlResponse.json();
            
            if (crawlData.success) {
                // 새로운 데이터 로드
                await this.loadPosts();
                await this.loadStats();
                this.showSuccess(crawlData.message);
            } else {
                this.showError(crawlData.message);
            }
            
        } catch (error) {
            console.error('데이터 새로고침 오류:', error);
            this.showError('데이터 새로고침에 실패했습니다.');
        } finally {
            this.showLoading(false);
        }
    }
    
    applyFilters() {
        let filtered = [...this.posts];
        
        // 사이트 필터
        if (this.currentFilters.site !== 'all') {
            filtered = filtered.filter(post => post.site === this.currentFilters.site);
        }
        
        // 검색 필터
        if (this.currentFilters.search) {
            const searchTerm = this.currentFilters.search.toLowerCase();
            filtered = filtered.filter(post => 
                post.title.toLowerCase().includes(searchTerm)
            );
        }
        
        // 정렬
        this.sortPosts(filtered);
        
        this.filteredPosts = filtered;
        this.currentPage = 1;
        this.renderPosts();
    }
    
    sortPosts(posts) {
        switch (this.currentFilters.sort) {
            case 'views':
                posts.sort((a, b) => (b.views || 0) - (a.views || 0));
                break;
            case 'likes':
                posts.sort((a, b) => (b.likes || 0) - (a.likes || 0));
                break;
            case 'latest':
            default:
                posts.sort((a, b) => new Date(b.crawled_at) - new Date(a.crawled_at));
                break;
        }
    }
    
    renderPosts() {
        const container = document.getElementById('postsContainer');
        const endIndex = this.currentPage * this.postsPerPage;
        const postsToShow = this.filteredPosts.slice(0, endIndex);
        
        container.innerHTML = '';
        
        if (postsToShow.length === 0) {
            container.innerHTML = '<div class="no-posts">검색 결과가 없습니다.</div>';
            this.hideLoadMoreButton();
            return;
        }
        
        postsToShow.forEach(post => {
            container.appendChild(this.createPostCard(post));
        });
        
        // 더 보기 버튼 표시/숨김
        if (endIndex < this.filteredPosts.length) {
            this.showLoadMoreButton();
        } else {
            this.hideLoadMoreButton();
        }
    }
    
    createPostCard(post) {
        const card = document.createElement('div');
        card.className = 'post-card';
        
        const siteNames = {
            'bobae': '보배드림',
            'ppomppu': '뽐뿌',
            'fmkorea': 'fmkorea',
            'dcinside': '디시인사이드'
        };
        
        card.innerHTML = `
            <div class="post-header">
                <span class="site-badge ${post.site}">${siteNames[post.site] || post.site}</span>
            </div>
            <div class="post-title">
                <a href="${post.url}" target="_blank" rel="noopener noreferrer">
                    ${this.escapeHtml(post.title)}
                </a>
            </div>
            <div class="post-meta">
                <span class="post-author">
                    <i class="fas fa-user"></i> ${this.escapeHtml(post.author || '익명')}
                </span>
                <div class="post-stats">
                    ${post.views && post.views > 0 ? `<span><i class="fas fa-eye"></i> ${this.formatNumber(post.views)}</span>` : ''}
                    ${post.likes && post.likes > 0 ? `<span><i class="fas fa-heart"></i> ${this.formatNumber(post.likes)}</span>` : ''}
                    ${post.comments && post.comments > 0 ? `<span><i class="fas fa-comment"></i> ${this.formatNumber(post.comments)}</span>` : ''}
                </div>
            </div>
        `;
        
        return card;
    }
    
    loadMorePosts() {
        this.currentPage++;
        this.renderPosts();
    }
    
    showLoadMoreButton() {
        document.getElementById('loadMoreBtn').classList.remove('hidden');
    }
    
    hideLoadMoreButton() {
        document.getElementById('loadMoreBtn').classList.add('hidden');
    }
    
    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.remove('hidden');
        } else {
            loading.classList.add('hidden');
        }
    }
    
    showError(message) {
        // 간단한 알림으로 대체 (실제로는 더 나은 UI 구현 가능)
        alert('오류: ' + message);
    }
    
    showSuccess(message) {
        // 간단한 알림으로 대체 (실제로는 더 나은 UI 구현 가능)
        alert('성공: ' + message);
    }
    
    updateLastUpdate() {
        const now = new Date();
        const timeString = now.toLocaleString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        document.getElementById('lastUpdate').textContent = timeString;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
}

// 페이지 로드 시 앱 시작
document.addEventListener('DOMContentLoaded', () => {
    new CommunityAggregator();
});