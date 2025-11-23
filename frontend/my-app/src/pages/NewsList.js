import React, { useEffect, useState, useCallback } from "react";
import { newsAPI } from "../services/api";
import "../styles/NewsList.css";

const NewsList = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const [generatingVideo, setGeneratingVideo] = useState({});
  const [videoStatus, setVideoStatus] = useState({});
  const [visibleCount, setVisibleCount] = useState(12);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        const response = await newsAPI.getAllNews();
        const newsData = response.data || [];
        setNews(newsData);
        checkAllVideoStatus(newsData);
      } catch (err) {
        setError("Failed to load news. Please try again later.");
        console.error("Error fetching news:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
  }, []);

  const checkAllVideoStatus = async (newsItems) => {
    const statusMap = {};
    const promises = newsItems.map(async (item) => {
      try {
        const response = await newsAPI.checkVideoExists(item.id);
        statusMap[item.id] = response.data.exists ? 'ready' : 'none';
      } catch (err) {
        console.log(`Error checking video for ${item.id}:`, err);
        statusMap[item.id] = 'none';
      }
    });

    await Promise.allSettled(promises);
    setVideoStatus(statusMap);
  };

  const categories = ["all", ...new Set(news.map(item => item.category).filter(Boolean))];

  const filteredAndSortedNews = news
    .filter(item => {
      const matchesSearch = item.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           item.description?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === "all" || item.category === selectedCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      const dateA = new Date(a.published_at || a.created_at || Date.now());
      const dateB = new Date(b.published_at || b.created_at || Date.now());
      return sortBy === "newest" ? dateB - dateA : dateA - dateB;
    });

  const visibleNews = filteredAndSortedNews.slice(0, visibleCount);

  const formatDate = (dateString) => {
    if (!dateString) return "Just now";

    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "Recently";

    const now = new Date();
    const diffMs = Math.abs(now - date);
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffHours < 1) return "Just now";
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return "1 day ago";
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: diffDays > 365 ? "numeric" : undefined
    });
  };

  const truncateText = (text, maxLength = 100) => {
    if (!text || typeof text !== 'string') return "";
    const trimmed = text.trim();
    return trimmed.length <= maxLength ? trimmed : trimmed.substring(0, maxLength) + "...";
  };

  const handleReadMore = useCallback((item, event) => {
    event.preventDefault();
    if (item.url) {
      window.open(item.url, '_blank', 'noopener,noreferrer');
    }
  }, []);

  const handleGenerateVideo = async (newsId, newsTitle) => {
  if (!newsId) {
    alert("Invalid news item");
    return;
  }

  try {
    // 1. Optimistically show "generating"
    setGeneratingVideo((prev) => ({ ...prev, [newsId]: true }));
    setVideoStatus((prev) => ({ ...prev, [newsId]: "generating" }));

    // 2. Fire and forget – we don't care about the exact response shape
    await newsAPI.generateVideoById(newsId);   // ← just await, no strict check

    // If we reach here → request was sent successfully (2xx status)
    console.log("Video generation request accepted for", newsId);

    // Start polling – this is the only source of truth now
    pollVideoStatus(newsId);
  } catch (err) {
    // Only REAL errors (network, 5xx, 4xx except 202/200) come here
    console.error("Failed to start video generation:", err);

    setVideoStatus((prev) => ({ ...prev, [newsId]: "none" }));
    setGeneratingVideo((prev) => ({ ...prev, [newsId]: false }));

    // Differentiate between real error and "unexpected success shape"
    if (err.response?.status >= 200 && err.response?.status < 300) {
      // It was actually accepted by the server → still poll!
      alert("Video generation started (server accepted). Checking status...");
      pollVideoStatus(newsId);
    } else {
      alert("Failed to generate video. Please try again.");
    }
  } finally {
    // Only disable the spinning button if we really failed
    // (in success case we keep "generating" until polling says ready)
    // → remove the blind reset here, or keep only on real failure
  }
};

  const pollVideoStatus = async (newsId, attempt = 1) => {
    if (attempt > 15) {
      console.log('Video generation timeout for news ID:', newsId);
      setVideoStatus(prev => ({ ...prev, [newsId]: 'none' }));
      alert('Video generation is taking longer than expected. Please try again later.');
      return;
    }

    try {
      const response = await newsAPI.checkVideoExists(newsId);
      if (response.data.exists) {
        setVideoStatus(prev => ({ ...prev, [newsId]: 'ready' }));
        console.log(`Video ready for news ID: ${newsId}`);
      } else {
        setTimeout(() => pollVideoStatus(newsId, attempt + 1), 2000);
      }
    } catch (err) {
      console.error('Error checking video status:', err);
      setTimeout(() => pollVideoStatus(newsId, attempt + 1), 2000);
    }
  };

  const handlePlayVideo = (newsId, newsTitle) => {
    const videoUrl = newsAPI.getVideoUrl(newsId);
    console.log(`Playing video for: ${newsTitle}`, videoUrl);
    window.open(videoUrl, '_blank', 'noopener,noreferrer');
  };

  const handleDownloadVideo = (newsId, newsTitle) => {
    const videoUrl = newsAPI.getVideoUrl(newsId);
    const link = document.createElement('a');
    link.href = videoUrl;
    link.download = `news-${newsTitle.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const loadMore = () => {
    setVisibleCount(prev => prev + 12);
  };

  const clearFilters = () => {
    setSearchTerm("");
    setSelectedCategory("all");
    setVisibleCount(12);
  };

  if (loading) {
    return (
      <div className="news-container premium-modern">
        <div className="loading-state premium-modern">
          <div className="loading-spinner premium-modern"></div>
          <p>Loading latest news...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="news-container premium-modern">
        <div className="error-state premium-modern">
          <div className="error-icon premium-modern">⚠️</div>
          <h3>Something went wrong</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-btn premium-modern">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="news-container premium-modern">
      {/* Premium Header */}
      <header className="news-header premium-modern">
        <h1 className="news-title premium-modern">News Dashboard</h1>
        {/* <p className="news-subtitle premium-modern">Stay informed with real-time news updates</p> */}
      </header>

      {/* Advanced Control Panel */}
      <section className="controls-section premium-modern">
        <div className="search-box premium-modern">
          <input
            type="text"
            placeholder="Search news headlines..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input premium-modern"
          />
          <span className="search-icon premium-modern">🔍</span>
        </div>

        <div className="filters-row premium-modern">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="filter-select premium-modern"
          >
            <option value="all">All Categories</option>
            {categories.filter(cat => cat !== "all").map(category => (
              <option key={category} value={category}>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="filter-select premium-modern"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>
        </div>
      </section>

      {/* Enhanced Results Info */}
      {filteredAndSortedNews.length > 0 && (
        <div className="results-info premium-modern">
          <span className="results-count">{filteredAndSortedNews.length} news items found</span>
          {(searchTerm || selectedCategory !== 'all') && (
            <span className="results-filters">
              {searchTerm && ` for "${searchTerm}"`}
              {selectedCategory !== 'all' && ` in ${selectedCategory}`}
              <button onClick={clearFilters} className="clear-filters-btn">Clear</button>
            </span>
          )}
        </div>
      )}

      {/* Premium News Grid */}
      <div className="news-grid premium-modern">
        {visibleNews.length === 0 ? (
          <div className="empty-state premium-modern">
            <div className="empty-icon">📰</div>
            <h3>No news found</h3>
            <p>Try adjusting your search or filters</p>
            <button onClick={clearFilters} className="clear-btn premium-modern">
              Clear All Filters
            </button>
          </div>
        ) : (
          visibleNews.map((item) => (
            <article key={item.id} className="news-card premium-modern">
              {item.image_url && (
                <div className="card-image premium-modern">
                  <img
                    src={item.image_url}
                    alt={item.title}
                    loading="lazy"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                </div>
              )}

              <div className="card-content premium-modern">
                <div className="card-header premium-modern">
                  <span className="source-badge premium-modern">
                    {item.source || 'News Source'}
                  </span>
                  <span className="publish-time premium-modern">
                    {formatDate(item.published_at)}
                  </span>
                </div>

                <h3 className="news-title-text premium-modern">
                  <a
                    href={item.url || '#'}
                    onClick={(e) => handleReadMore(item, e)}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {truncateText(item.title, 80)}
                  </a>
                </h3>

                {item.description && (
                  <p className="news-description premium-modern">
                    {truncateText(item.description, 120)}
                  </p>
                )}
              </div>

              {/* Enhanced Footer with Video Actions */}
              <div className="card-footer premium-modern">
                <div className="footer-actions">
                  <a
                    href={item.url || '#'}
                    onClick={(e) => handleReadMore(item, e)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="read-btn premium-modern"
                  >
                    Read Article
                  </a>

                  <div className="video-actions">
                    {videoStatus[item.id] === 'ready' ? (
                      <div className="video-ready-actions">
                        <button
                          onClick={() => handlePlayVideo(item.id, item.title)}
                          className="play-video-btn premium-modern"
                          title="Play generated video"
                        >
                          <span className="video-icon">🎥</span>
                          Play Video
                        </button>
                        <button
                          onClick={() => handleDownloadVideo(item.id, item.title)}
                          className="download-video-btn premium-modern"
                          title="Download video"
                        >
                          <span className="download-icon">⬇️</span>
                        </button>
                      </div>
                    ) : videoStatus[item.id] === 'generating' ? (
                      <button
                        disabled
                        className="generate-video-btn premium-modern generating"
                      >
                        <span className="spinner-small"></span>
                        Creating Video...
                      </button>
                    ) : (
                      <button
                        onClick={() => handleGenerateVideo(item.id, item.title)}
                        disabled={generatingVideo[item.id]}
                        className="generate-video-btn premium-modern"
                        title="Generate video from this news"
                      >
                        <span className="video-icon">🎬</span>
                        Create Video
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </article>
          ))
        )}
      </div>

      {/* Load More Button */}
      {visibleNews.length < filteredAndSortedNews.length && (
        <div className="load-more-section premium-modern">
          <button onClick={loadMore} className="load-more-btn premium-modern">
            Load More News ({filteredAndSortedNews.length - visibleNews.length} remaining)
          </button>
        </div>
      )}
    </div>
  );
};

export default NewsList;