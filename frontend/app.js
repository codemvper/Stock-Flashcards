// A股上市公司闪卡 - 前端应用逻辑

// 配置
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : window.location.origin;

// 状态管理
let currentStock = null;
let viewedStocks = [];
let favoriteStocks = [];
let isFlipped = false;
let isAnimating = false;
let touchStartX = 0;
let touchEndX = 0;
let hasShownGuide = false;

// DOM元素
const elements = {
    card: document.getElementById('stockCard'),
    cardContainer: document.getElementById('cardContainer'),
    loading: document.getElementById('loading'),
    
    // 正面元素
    companyName: document.getElementById('companyName'),
    companyLogo: document.getElementById('companyLogo'),
    stockCode: document.getElementById('stockCode'),
    stockPrice: document.getElementById('stockPrice'),
    priceChange: document.getElementById('priceChange'),
    marketValue: document.getElementById('marketValue'),
    holderNum: document.getElementById('holderNum'),
    holderAvg: document.getElementById('holderAvg'),
    industryTag: document.getElementById('industryTag'),
    businessDesc: document.getElementById('businessDesc'),
    
    // 财务指标元素
    roeValue: document.getElementById('roeValue'),
    roeProgress: document.getElementById('roeProgress'),
    roeDesc: document.getElementById('roeDesc'),
    peValue: document.getElementById('peValue'),
    peProgress: document.getElementById('peProgress'),
    peDesc: document.getElementById('peDesc'),
    pbValue: document.getElementById('pbValue'),
    pbProgress: document.getElementById('pbProgress'),
    pbDesc: document.getElementById('pbDesc'),
    grossProfitMarginValue: document.getElementById('grossProfitMarginValue'),
    grossProfitMarginProgress: document.getElementById('grossProfitMarginProgress'),
    grossProfitMarginDesc: document.getElementById('grossProfitMarginDesc'),
    debtToAssetRatioValue: document.getElementById('debtToAssetRatioValue'),
    debtToAssetRatioProgress: document.getElementById('debtToAssetRatioProgress'),
    debtToAssetRatioDesc: document.getElementById('debtToAssetRatioDesc'),
    
    // 统计元素
    viewedCount: document.getElementById('viewedCount'),
    favoriteCount: document.getElementById('favoriteCount'),
    favoriteBadge: document.getElementById('favoriteBadge'),
    
    // 按钮
    likeBtn: document.getElementById('likeBtn'),
    dislikeBtn: document.getElementById('dislikeBtn'),
    shuffleBtn: document.getElementById('shuffleBtn'),
    favoritesBtn: document.getElementById('favoritesBtn'),
    
    // 模态框
    favoritesModal: document.getElementById('favoritesModal'),
    favoritesList: document.getElementById('favoritesList'),
    closeModal: document.getElementById('closeModal'),
    
    // 引导
    guideOverlay: document.getElementById('guideOverlay'),
    guideStep1: document.getElementById('guideStep1'),
    guideStep2: document.getElementById('guideStep2'),
};

// 初始化
function init() {
    loadLocalData();
    updateStats();
    setupEventListeners();
    loadRandomStock();
    
    // 检查是否需要显示引导
    if (!localStorage.getItem('hasSeenGuide')) {
        showGuide();
    }
}

// 加载本地数据
function loadLocalData() {
    const viewed = localStorage.getItem('viewedStocks');
    const favorites = localStorage.getItem('favoriteStocks');
    
    if (viewed) {
        try {
            viewedStocks = JSON.parse(viewed);
        } catch (e) {
            viewedStocks = [];
        }
    }
    
    if (favorites) {
        try {
            favoriteStocks = JSON.parse(favorites);
        } catch (e) {
            favoriteStocks = [];
        }
    }
}

// 保存本地数据
function saveLocalData() {
    localStorage.setItem('viewedStocks', JSON.stringify(viewedStocks));
    localStorage.setItem('favoriteStocks', JSON.stringify(favoriteStocks));
}

// 更新统计信息
function updateStats() {
    elements.viewedCount.textContent = viewedStocks.length;
    elements.favoriteCount.textContent = favoriteStocks.length;
    elements.favoriteBadge.textContent = favoriteStocks.length;
}

// 设置事件监听
function setupEventListeners() {
    // 卡片翻转
    elements.card.addEventListener('click', handleCardClick);
    
    // 按钮事件
    elements.likeBtn.addEventListener('click', handleLike);
    elements.dislikeBtn.addEventListener('click', handleDislike);
    elements.shuffleBtn.addEventListener('click', handleShuffle);
    elements.favoritesBtn.addEventListener('click', showFavorites);
    elements.closeModal.addEventListener('click', hideFavorites);
    
    // 模态框背景点击关闭
    elements.favoritesModal.addEventListener('click', (e) => {
        if (e.target === elements.favoritesModal) {
            hideFavorites();
        }
    });
    
    // 引导点击关闭
    elements.guideOverlay.addEventListener('click', skipGuide);
    
    // 触摸事件（滑动）
    elements.cardContainer.addEventListener('touchstart', handleTouchStart, { passive: true });
    elements.cardContainer.addEventListener('touchend', handleTouchEnd, { passive: true });
    
    // 键盘事件
    document.addEventListener('keydown', handleKeyPress);
}

// 处理卡片点击
function handleCardClick(e) {
    if (isAnimating) return;
    
    isFlipped = !isFlipped;
    elements.card.classList.toggle('flipped', isFlipped);
    
    // 引导：第一次翻转后显示第二步
    if (!hasShownGuide && !localStorage.getItem('hasSeenGuide')) {
        hasShownGuide = true; // 标记已显示过引导
        setTimeout(() => {
            elements.guideStep1.classList.add('hidden');
            elements.guideStep2.classList.remove('hidden');
        }, 600);
    }
}

// 处理触摸开始
function handleTouchStart(e) {
    touchStartX = e.changedTouches[0].screenX;
}

// 处理触摸结束
function handleTouchEnd(e) {
    if (isAnimating) return;
    
    touchEndX = e.changedTouches[0].screenX;
    const diff = touchEndX - touchStartX;
    
    if (Math.abs(diff) > 100) { // 滑动阈值
        if (diff > 0) {
            handleLike();
        } else {
            handleDislike();
        }
    }
}

// 处理键盘事件
function handleKeyPress(e) {
    if (isAnimating) return;
    
    switch(e.key) {
        case 'ArrowLeft':
            handleDislike();
            break;
        case 'ArrowRight':
            handleLike();
            break;
        case ' ':
            handleCardClick();
            break;
    }
}

// 收藏
function handleLike() {
    if (isAnimating || !currentStock) return;
    
    isAnimating = true;
    elements.card.classList.add('swipe-right');
    
    // 添加到收藏
    if (!favoriteStocks.find(s => s.ts_code === currentStock.ts_code)) {
        favoriteStocks.push({
            ts_code: currentStock.ts_code,
            name: currentStock.name,
            code: currentStock.code,
            time: new Date().toISOString()
        });
        saveLocalData();
        updateStats();
    }
    
    // 完成引导
    completeGuide();
    
    setTimeout(() => {
        elements.card.classList.remove('swipe-right');
        isAnimating = false;
        if (isFlipped) {
            isFlipped = false;
            elements.card.classList.remove('flipped');
        }
        loadRandomStock();
    }, 500);
}

// 放弃
function handleDislike() {
    if (isAnimating || !currentStock) return;
    
    isAnimating = true;
    elements.card.classList.add('swipe-left');
    
    // 完成引导
    completeGuide();
    
    setTimeout(() => {
        elements.card.classList.remove('swipe-left');
        isAnimating = false;
        if (isFlipped) {
            isFlipped = false;
            elements.card.classList.remove('flipped');
        }
        loadRandomStock();
    }, 500);
}

// 重新洗牌
function handleShuffle() {
    if (!confirm('确定要重新开始吗？这将清空浏览记录和收藏列表。')) {
        return;
    }
    
    viewedStocks = [];
    favoriteStocks = [];
    saveLocalData();
    updateStats();
    loadRandomStock();
}

// 显示收藏列表
function showFavorites() {
    if (favoriteStocks.length === 0) {
        elements.favoritesList.innerHTML = '<p class="empty-message">还没有收藏任何公司</p>';
    } else {
        elements.favoritesList.innerHTML = favoriteStocks.map(stock => `
            <div class="favorite-item" data-ts-code="${stock.ts_code}">
                <div class="favorite-info">
                    <div class="favorite-name">${stock.name}</div>
                    <div class="favorite-code">${stock.code}</div>
                </div>
                <button class="remove-favorite-btn" onclick="removeFavorite('${stock.ts_code}')">
                    取消收藏
                </button>
            </div>
        `).join('');
    }
    
    elements.favoritesModal.classList.add('show');
}

// 隐藏收藏列表
function hideFavorites() {
    elements.favoritesModal.classList.remove('show');
}

// 移除收藏
window.removeFavorite = function(ts_code) {
    favoriteStocks = favoriteStocks.filter(s => s.ts_code !== ts_code);
    saveLocalData();
    updateStats();
    showFavorites(); // 刷新列表
};

// 加载随机股票
async function loadRandomStock() {
    try {
        elements.loading.classList.remove('hidden');
        elements.card.style.opacity = '0';
        
        const viewedParam = viewedStocks.map(s => s.ts_code || s).join(',');
        const apiUrl = `${API_BASE_URL}/api/random-stock?viewed=${viewedParam}`;
        console.log('正在请求API:', apiUrl);
        
        const response = await fetch(apiUrl);
        console.log('API响应状态:', response.status);
        
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            try {
                const error = await response.json();
                if (error.all_viewed) {
                    alert('恭喜！您已经浏览完所有股票了！');
                    return;
                }
                errorMessage = error.error || errorMessage;
            } catch (e) {
                console.error('解析错误响应失败:', e);
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        console.log('获取到股票数据:', data);
        currentStock = data;
        
        // 添加到已浏览列表
        if (!viewedStocks.includes(data.ts_code)) {
            viewedStocks.push(data.ts_code);
            saveLocalData();
            updateStats();
        }
        
        // 更新UI
        updateCardUI(data);
        
        elements.loading.classList.add('hidden');
        elements.card.style.opacity = '1';
    } catch (error) {
        console.error('加载股票失败:', error);
        elements.loading.classList.add('hidden');
        
        // 显示更详细的错误信息
        let errorMsg = '加载失败，请检查：\n';
        if (error.message.includes('Failed to fetch')) {
            errorMsg += '1. 后端服务是否启动 (python run.py)\n';
            errorMsg += '2. 端口5000是否被占用\n';
            errorMsg += '3. 网络连接是否正常';
        } else {
            errorMsg += error.message;
        }
        alert(errorMsg);
    }
}

// 更新卡片UI
function updateCardUI(data) {
    
    // 正面信息
    elements.companyName.textContent = data.name;
    elements.companyLogo.src = data.logo_url || '';
    elements.companyLogo.style.display = data.logo_url ? 'block' : 'none';
    elements.stockCode.textContent = data.code;
    elements.stockPrice.textContent = data.price.toFixed(2);
    
    // 涨跌幅
    const changeValue = data.pct_chg;
    const changeClass = changeValue > 0 ? 'positive' : changeValue < 0 ? 'negative' : 'neutral';
    const changeSymbol = changeValue > 0 ? '+' : '';
    
    elements.priceChange.className = `price-change ${changeClass}`;
    elements.priceChange.innerHTML = `
        <span class="change-percent">${changeSymbol}${changeValue.toFixed(2)}%</span>
    `;
    
    elements.marketValue.textContent = `${data.market_value.toFixed(2)} 亿`;
    
    // 股东信息
    if (data.holder && data.holder.holder_num) {
        elements.holderNum.textContent = data.holder.holder_num.toLocaleString();
        const avgAmount = data.holder.holder_avg_amount;
        if (avgAmount >= 10000) {
            elements.holderAvg.textContent = `${(avgAmount / 10000).toFixed(2)} 万元`;
        } else {
            elements.holderAvg.textContent = `${avgAmount.toFixed(2)} 万元`;
        }
    } else {
        elements.holderNum.textContent = '---';
        elements.holderAvg.textContent = '---';
    }
    
    elements.industryTag.textContent = data.industry || '未分类';
    
    // 主营业务描述
    const business = data.main_business || data.business_scope || data.introduction || '暂无业务描述';
    // 截取前100个字符
    elements.businessDesc.textContent = business.length > 100 ? business.substring(0, 100) + '...' : business;
    
    // 财务数据
    const financial = data.financial;
    const historical = data.historical_comparison || {};
    
    // ROE
    const roe = financial.roe || 0;
    elements.roeValue.textContent = `${roe.toFixed(2)}%`;
    
    if (historical.roe) {
        // 使用历史比较数据
        const roeComparison = historical.roe;
        elements.roeProgress.style.width = `${roeComparison.percentile}%`;
        
        // 根据表现设置颜色
        if (roeComparison.vs_avg > 20) {
            elements.roeProgress.style.backgroundColor = '#10b981'; // 绿色：优秀
        } else if (roeComparison.vs_avg > -20) {
            elements.roeProgress.style.backgroundColor = '#f59e0b'; // 黄色：一般
        } else {
            elements.roeProgress.style.backgroundColor = '#ef4444'; // 红色：较差
        }
        
        elements.roeDesc.textContent = `vs 5年均值 ${roeComparison.vs_avg > 0 ? '+' : ''}${roeComparison.vs_avg}%`;
    } else {
        // 回退到原有逻辑
        elements.roeProgress.style.width = `${Math.min(Math.abs(roe), 100)}%`;
        elements.roeProgress.style.backgroundColor = '#8b5cf6';
        elements.roeDesc.textContent = `${roe > 0 ? '正值' : roe < 0 ? '负值' : '持平'}`;
    }
    
    // PE
    const pe = financial.pe || 0;
    elements.peValue.textContent = pe.toFixed(2);
    
    if (historical.pe) {
        // 使用历史比较数据
        const peComparison = historical.pe;
        elements.peProgress.style.width = `${peComparison.percentile}%`;
        
        // 根据表现设置颜色（PE越低越好）
        if (peComparison.vs_avg < -20) {
            elements.peProgress.style.backgroundColor = '#10b981'; // 绿色：优秀（低PE）
        } else if (peComparison.vs_avg < 20) {
            elements.peProgress.style.backgroundColor = '#f59e0b'; // 黄色：一般
        } else {
            elements.peProgress.style.backgroundColor = '#ef4444'; // 红色：较差（高PE）
        }
        
        elements.peDesc.textContent = `vs 5年均值 ${peComparison.vs_avg > 0 ? '+' : ''}${peComparison.vs_avg}%`;
    } else {
        // 回退到原有逻辑
        const pePercent = Math.min((pe / 100) * 100, 100);
        elements.peProgress.style.width = `${pePercent}%`;
        elements.peProgress.style.backgroundColor = '#8b5cf6';
        elements.peDesc.textContent = pe > 0 ? `市盈率 ${pe.toFixed(2)}` : '暂无数据';
    }
    
    // PB
    const pb = financial.pb || 0;
    elements.pbValue.textContent = pb.toFixed(2);
    
    if (historical.pb) {
        // 使用历史比较数据
        const pbComparison = historical.pb;
        elements.pbProgress.style.width = `${pbComparison.percentile}%`;
        
        // 根据表现设置颜色（PB越低越好）
        if (pbComparison.vs_avg < -20) {
            elements.pbProgress.style.backgroundColor = '#10b981'; // 绿色：优秀（低PB）
        } else if (pbComparison.vs_avg < 20) {
            elements.pbProgress.style.backgroundColor = '#f59e0b'; // 黄色：一般
        } else {
            elements.pbProgress.style.backgroundColor = '#ef4444'; // 红色：较差（高PB）
        }
        
        elements.pbDesc.textContent = `vs 5年均值 ${pbComparison.vs_avg > 0 ? '+' : ''}${pbComparison.vs_avg}%`;
    } else {
        // 回退到原有逻辑
        const pbPercent = Math.min((pb / 10) * 100, 100);
        elements.pbProgress.style.width = `${pbPercent}%`;
        elements.pbProgress.style.backgroundColor = '#8b5cf6';
        elements.pbDesc.textContent = pb > 0 ? `市净率 ${pb.toFixed(2)}` : '暂无数据';
    }
    
    // 毛利率
    const grossProfitMargin = financial.gross_profit_margin || 0;
    elements.grossProfitMarginValue.textContent = `${grossProfitMargin.toFixed(2)}%`;
    
    if (historical.gross_profit_margin) {
        // 使用历史比较数据
        const marginComparison = historical.gross_profit_margin;
        elements.grossProfitMarginProgress.style.width = `${marginComparison.percentile}%`;
        
        // 根据表现设置颜色（毛利率越高越好）
        if (marginComparison.vs_avg > 20) {
            elements.grossProfitMarginProgress.style.backgroundColor = '#10b981'; // 绿色：优秀（高毛利率）
        } else if (marginComparison.vs_avg > -20) {
            elements.grossProfitMarginProgress.style.backgroundColor = '#f59e0b'; // 黄色：一般
        } else {
            elements.grossProfitMarginProgress.style.backgroundColor = '#ef4444'; // 红色：较差（低毛利率）
        }
        
        elements.grossProfitMarginDesc.textContent = `vs 5年均值 ${marginComparison.vs_avg > 0 ? '+' : ''}${marginComparison.vs_avg}%`;
    } else {
        // 回退到原有逻辑
        const marginPercent = Math.min(grossProfitMargin, 100);
        elements.grossProfitMarginProgress.style.width = `${marginPercent}%`;
        elements.grossProfitMarginProgress.style.backgroundColor = '#8b5cf6';
        elements.grossProfitMarginDesc.textContent = grossProfitMargin > 0 ? `毛利率 ${grossProfitMargin.toFixed(2)}%` : '暂无数据';
    }
    
    // 资产负债率
    const debtToAssetRatio = financial.debt_to_asset_ratio || 0;
    elements.debtToAssetRatioValue.textContent = `${debtToAssetRatio.toFixed(2)}%`;
    
    if (historical.debt_to_asset_ratio) {
        // 使用历史比较数据
        const debtComparison = historical.debt_to_asset_ratio;
        elements.debtToAssetRatioProgress.style.width = `${debtComparison.percentile}%`;
        
        // 根据表现设置颜色（资产负债率适中最好，过高或过低都不好）
        const avgDiff = Math.abs(debtComparison.vs_avg);
        if (avgDiff <= 10) {
            elements.debtToAssetRatioProgress.style.backgroundColor = '#10b981'; // 绿色：适中
        } else if (avgDiff <= 30) {
            elements.debtToAssetRatioProgress.style.backgroundColor = '#f59e0b'; // 黄色：一般
        } else {
            elements.debtToAssetRatioProgress.style.backgroundColor = '#ef4444'; // 红色：偏离较大
        }
        
        elements.debtToAssetRatioDesc.textContent = `vs 5年均值 ${debtComparison.vs_avg > 0 ? '+' : ''}${debtComparison.vs_avg}%`;
    } else {
        // 回退到原有逻辑
        const debtPercent = Math.min(debtToAssetRatio, 100);
        elements.debtToAssetRatioProgress.style.width = `${debtPercent}%`;
        elements.debtToAssetRatioProgress.style.backgroundColor = '#8b5cf6';
        elements.debtToAssetRatioDesc.textContent = debtToAssetRatio > 0 ? `资产负债率 ${debtToAssetRatio.toFixed(2)}%` : '暂无数据';
    }
}

// 显示引导
function showGuide() {
    hasShownGuide = false;
    elements.guideOverlay.classList.remove('hidden');
    elements.guideStep1.classList.remove('hidden');
    elements.guideStep2.classList.add('hidden');
}

// 完成引导
function completeGuide() {
    if (!localStorage.getItem('hasSeenGuide')) {
        localStorage.setItem('hasSeenGuide', 'true');
    }
    // 立即隐藏引导
    elements.guideOverlay.classList.add('hidden');
}

// 跳过引导（点击引导区域）
function skipGuide() {
    localStorage.setItem('hasSeenGuide', 'true');
    elements.guideOverlay.classList.add('hidden');
}



// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

