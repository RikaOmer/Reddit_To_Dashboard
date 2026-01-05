import { useState, useEffect, useMemo } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const CATEGORY_COLORS = {
  'Pricing': '#f59e0b',
  'Performance': '#10b981',
  'Support': '#3b82f6',
  'Features': '#8b5cf6',
  'Integration': '#ec4899',
  'User Experience': '#06b6d4',
  'General Discussion': '#6b7280',
  'Complaints': '#ef4444',
  'Recommendations': '#22c55e',
}

const ALL_TOPICS = [
  'All Topics',
  'Pricing',
  'Performance',
  'Support',
  'Features',
  'Integration',
  'User Experience',
  'General Discussion',
  'Complaints',
  'Recommendations'
]

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [loadingMessage, setLoadingMessage] = useState('')
  
  // Filter states
  const [selectedEntity, setSelectedEntity] = useState('All')
  const [selectedTopic, setSelectedTopic] = useState('All Topics')

  const API_BASE = 'http://localhost:8080'

  const fetchRankings = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/rankings`)
      const result = await response.json()
      if (result.success && result.data) {
        setData(result.data)
        setLastUpdated(result.last_updated)
      }
    } catch (error) {
      console.error('Error fetching rankings:', error)
    }
  }

  const refreshData = async () => {
    setLoading(true)
    setLoadingMessage('Fetching Reddit posts...')
    
    try {
      setTimeout(() => setLoadingMessage('Validating with AI...'), 3000)
      setTimeout(() => setLoadingMessage('Generating rankings...'), 8000)
      
      const response = await fetch(`${API_BASE}/api/refresh`, { method: 'POST' })
      const result = await response.json()
      
      if (result.success) {
        setData(result.data)
        setLastUpdated(result.last_updated)
      } else {
        alert(result.message || 'Failed to refresh data')
      }
    } catch (error) {
      console.error('Error refreshing:', error)
      alert('Failed to refresh data. Is the API running?')
    } finally {
      setLoading(false)
      setLoadingMessage('')
    }
  }

  useEffect(() => {
    fetchRankings()
  }, [])

  const formatDate = (isoString) => {
    if (!isoString) return ''
    const date = new Date(isoString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getCategoryColor = (category) => {
    return CATEGORY_COLORS[category] || '#6b7280'
  }

  // Get all brands for entity filter
  const brands = useMemo(() => {
    if (!data) return []
    return ['All', ...Object.keys(data)]
  }, [data])

  // Get filtered data based on selected entity and topic
  const filteredData = useMemo(() => {
    if (!data) return null
    
    let result = {}
    
    // Filter by entity
    if (selectedEntity === 'All') {
      result = { ...data }
    } else {
      result = { [selectedEntity]: data[selectedEntity] }
    }
    
    // Filter by topic within each brand
    if (selectedTopic !== 'All Topics') {
      const filtered = {}
      for (const [brand, brandData] of Object.entries(result)) {
        const filteredAllPosts = (brandData.all_posts || []).filter(post => {
          const subject = post.validation?.subject || 'General Discussion'
          return subject === selectedTopic
        })
        const filteredTopPosts = brandData.top_posts.filter(post => {
          const subject = post.validation?.subject || 'General Discussion'
          return subject === selectedTopic
        })
        
        filtered[brand] = {
          ...brandData,
          all_posts: filteredAllPosts,
          top_posts: filteredTopPosts,
          total_posts: filteredAllPosts.length
        }
      }
      result = filtered
    }
    
    return result
  }, [data, selectedEntity, selectedTopic])

  // Get all posts for trends chart (use all_posts to show all 30 posts)
  const allPosts = useMemo(() => {
    if (!filteredData) return []
    
    const posts = []
    for (const [brand, brandData] of Object.entries(filteredData)) {
      // Use all_posts for the chart, fallback to top_posts
      const postsArray = brandData.all_posts || brandData.top_posts
      for (const post of postsArray) {
        posts.push({
          ...post,
          brand,
          date: new Date(post.created_utc).getTime(),
          displayDate: post.date || post.created_utc
        })
      }
    }
    return posts.sort((a, b) => a.date - b.date)
  }, [filteredData])

  // Get top 3 newest posts
  const newestPosts = useMemo(() => {
    if (!allPosts.length) return []
    return [...allPosts].sort((a, b) => b.date - a.date).slice(0, 3)
  }, [allPosts])

  return (
    <div className="app">
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <div className="loading-text">{loadingMessage}</div>
          <div className="loading-subtext">This may take a minute...</div>
        </div>
      )}

      <header className="header">
        <div className="logo">
          <div className="logo-icon">R</div>
          <h1>Reddit <span>Dashboard</span></h1>
        </div>
        <div className="header-actions">
          {lastUpdated && (
            <span className="last-updated">
              Updated: {formatDate(lastUpdated)}
            </span>
          )}
          <button 
            className={`refresh-btn ${loading ? 'loading' : ''}`}
            onClick={refreshData}
            disabled={loading}
          >
            <svg className="refresh-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M23 4v6h-6M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            {loading ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>
      </header>

      <main className="main-content">
        {!data ? (
          <div className="empty-state">
            <div className="empty-state-icon">📊</div>
            <h2>No Data Yet</h2>
            <p>Click the refresh button to fetch Reddit posts and generate rankings</p>
            <button className="refresh-btn" onClick={refreshData} disabled={loading}>
              <svg className="refresh-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M23 4v6h-6M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
              Fetch Data Now
            </button>
          </div>
        ) : (
          <>
            {/* Filters */}
            <div className="filters-bar">
              <div className="filter-group">
                <label>Entity</label>
                <select 
                  value={selectedEntity} 
                  onChange={(e) => setSelectedEntity(e.target.value)}
                  className="filter-select"
                >
                  {brands.map(brand => (
                    <option key={brand} value={brand}>{brand}</option>
                  ))}
                </select>
              </div>
              <div className="filter-group">
                <label>Topic</label>
                <select 
                  value={selectedTopic} 
                  onChange={(e) => setSelectedTopic(e.target.value)}
                  className="filter-select"
                >
                  {ALL_TOPICS.map(topic => (
                    <option key={topic} value={topic}>{topic}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Trends Chart */}
            <TrendsChart posts={allPosts} getCategoryColor={getCategoryColor} />

            {/* Top Row: Newest Posts + Stats */}
            <div className="top-row-grid">
              <NewestPosts posts={newestPosts} getCategoryColor={getCategoryColor} />
            </div>

            {/* Brand Sections */}
            {Object.entries(filteredData).map(([brand, brandData]) => (
              <BrandSection 
                key={brand} 
                brand={brand} 
                data={brandData}
                getCategoryColor={getCategoryColor}
              />
            ))}
          </>
        )}
      </main>
    </div>
  )
}

function TrendsChart({ posts, getCategoryColor }) {
  if (!posts.length) return null

  // Sort by date and create chart data with index for even spacing
  const sortedPosts = [...posts].sort((a, b) => a.date - b.date)
  const chartData = sortedPosts.map((post, index) => ({
    index,
    date: post.date,
    score: post.engagement_score || 0,
    title: post.title?.substring(0, 50) + '...',
    brand: post.brand,
    category: post.validation?.subject || 'General',
    displayDate: new Date(post.date).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: '2-digit'
    })
  }))

  // Generate evenly spaced ticks (show ~6 labels)
  const tickCount = Math.min(6, chartData.length)
  const tickInterval = Math.floor(chartData.length / tickCount)
  const ticks = []
  for (let i = 0; i < chartData.length; i += tickInterval) {
    ticks.push(i)
  }
  if (ticks[ticks.length - 1] !== chartData.length - 1) {
    ticks.push(chartData.length - 1)
  }

  const formatXAxis = (index) => {
    if (chartData[index]) {
      return chartData[index].displayDate
    }
    return ''
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="chart-tooltip">
          <p className="tooltip-title">{data.title}</p>
          <p className="tooltip-score">Score: {data.score.toFixed(1)}</p>
          <p className="tooltip-date">{data.displayDate}</p>
          <p className="tooltip-brand">{data.brand} • {data.category}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="trends-card">
      <h3>📈 Engagement Trends Over Time ({chartData.length} posts)</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData} margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8e4de" />
            <XAxis 
              dataKey="index"
              type="number"
              domain={[0, chartData.length - 1]}
              ticks={ticks}
              tickFormatter={formatXAxis}
              stroke="#888888"
              fontSize={11}
              interval={0}
            />
            <YAxis 
              dataKey="score" 
              stroke="#888888"
              fontSize={12}
              label={{ value: 'Engagement Score', angle: -90, position: 'insideLeft', fill: '#888888' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line 
              type="monotone"
              dataKey="score"
              stroke="#ff6b5b"
              strokeWidth={2}
              dot={{ fill: '#ff6b5b', strokeWidth: 2, r: 5 }}
              activeDot={{ r: 8, fill: '#ff8a7a' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function NewestPosts({ posts, getCategoryColor }) {
  if (!posts.length) return null

  const formatPostDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="newest-posts-card">
      <h3>🆕 Top 3 Newest Posts</h3>
      <div className="newest-posts-list">
        {posts.map((post, index) => {
          const subject = post.validation?.subject || 'General'
          const sentiment = (post.validation?.sentiment || 'neutral').toLowerCase()
          
          return (
            <div key={post.id || index} className="newest-post-item">
              <div className="newest-post-rank">{index + 1}</div>
              <div className="newest-post-content">
                <div className="newest-post-title">{post.title}</div>
                <div className="newest-post-meta">
                  <span className="newest-post-date">{formatPostDate(post.displayDate)}</span>
                  <span className="newest-post-brand">{post.brand}</span>
                  <span 
                    className="newest-post-category"
                    style={{ color: getCategoryColor(subject) }}
                  >
                    {subject}
                  </span>
                </div>
              </div>
              <div className="newest-post-score">
                ⚡ {post.engagement_score?.toFixed(1) || '0'}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function BrandSection({ brand, data, getCategoryColor }) {
  const getBrandBadge = (brand) => {
    return brand.charAt(0).toUpperCase()
  }

  return (
    <section className="brand-section">
      <div className="brand-header">
        <div className={`brand-badge ${brand.toLowerCase()}`}>
          {getBrandBadge(brand)}
        </div>
        <div className="brand-title">
          <h2>{brand}</h2>
          <span className="post-count">{data.total_posts} posts analyzed</span>
        </div>
      </div>

      <div className="stats-grid">
        <CategoryDistribution 
          distribution={data.category_distribution} 
          getCategoryColor={getCategoryColor}
        />
        <SentimentOverview 
          distribution={data.category_distribution}
        />
      </div>

      <div className="posts-section">
        <h3>🏆 Top Posts by Engagement</h3>
        <div className="posts-grid">
          {data.top_posts.slice(0, 5).map((post, index) => (
            <PostCard 
              key={post.id || index} 
              post={post} 
              rank={index + 1}
              getCategoryColor={getCategoryColor}
            />
          ))}
        </div>
      </div>

      {Object.keys(data.top_posts_by_category || {}).length > 0 && (
        <div className="category-posts-section">
          <h3>📂 Top Posts by Category</h3>
          {Object.entries(data.top_posts_by_category).map(([category, posts]) => (
            <div key={category} className="category-group">
              <div className="category-group-header">{category}</div>
              <div className="posts-grid">
                {posts.map((post, index) => (
                  <PostCard 
                    key={post.id || index} 
                    post={post}
                    getCategoryColor={getCategoryColor}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

function CategoryDistribution({ distribution, getCategoryColor }) {
  const categories = Object.entries(distribution || {})
  if (!categories.length) return null
  
  const maxPercentage = Math.max(...categories.map(([_, stats]) => stats.percentage), 1)

  return (
    <div className="stat-card">
      <h3>📂 Category Distribution</h3>
      {categories.map(([category, stats]) => (
        <div key={category} className="category-item">
          <span className="category-name">{category}</span>
          <div className="category-stats">
            <span className="category-count">{stats.count} ({stats.percentage}%)</span>
            <div className="category-bar">
              <div 
                className="category-bar-fill"
                style={{ 
                  width: `${(stats.percentage / maxPercentage) * 100}%`,
                  backgroundColor: getCategoryColor(category)
                }}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

function SentimentOverview({ distribution }) {
  if (!distribution || !Object.keys(distribution).length) return null
  
  let totalPositive = 0, totalNegative = 0, totalNeutral = 0, totalMixed = 0, totalCount = 0

  Object.values(distribution).forEach(stats => {
    const count = stats.count
    totalCount += count
    totalPositive += (stats.sentiment_breakdown?.positive / 100) * count || 0
    totalNegative += (stats.sentiment_breakdown?.negative / 100) * count || 0
    totalNeutral += (stats.sentiment_breakdown?.neutral / 100) * count || 0
    totalMixed += (stats.sentiment_breakdown?.mixed / 100) * count || 0
  })

  const sentiments = [
    { name: 'positive', value: Math.round(totalPositive), icon: '😊' },
    { name: 'negative', value: Math.round(totalNegative), icon: '😞' },
    { name: 'neutral', value: Math.round(totalNeutral), icon: '😐' },
    { name: 'mixed', value: Math.round(totalMixed), icon: '🤔' },
  ].filter(s => s.value > 0)

  return (
    <div className="stat-card">
      <h3>💬 Sentiment Overview</h3>
      <div className="sentiment-grid">
        {sentiments.map(sentiment => (
          <div key={sentiment.name} className={`sentiment-pill ${sentiment.name}`}>
            <span>{sentiment.icon}</span>
            <span>{sentiment.name}</span>
            <strong>{sentiment.value}</strong>
          </div>
        ))}
      </div>
    </div>
  )
}

function PostCard({ post, rank, getCategoryColor }) {
  const validation = post.validation || {}
  const sentiment = (validation.sentiment || 'neutral').toLowerCase()
  const subject = validation.subject || 'General'
  const score = post.engagement_score?.toFixed(1) || '0'

  return (
    <div className="post-card">
      <div className="post-header">
        <span className="post-title">
          {rank && <strong>#{rank} </strong>}
          {post.title || 'Untitled'}
        </span>
        <span className="post-score">
          ⚡ {score}
        </span>
      </div>
      <div className="post-meta">
        <span className="post-tag category" style={{ backgroundColor: `${getCategoryColor(subject)}15`, color: getCategoryColor(subject) }}>
          {subject}
        </span>
        <span className={`post-tag sentiment ${sentiment}`}>
          {sentiment}
        </span>
        {post.permalink && (
          <a 
            href={post.permalink} 
            target="_blank" 
            rel="noopener noreferrer"
            className="post-link"
          >
            View on Reddit →
          </a>
        )}
      </div>
    </div>
  )
}

export default App
