import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const newsAPI = {
    fetchNews: (category = 'general') => api.post('/fetch-news/', { category }),
    fetchNewsScript: (category = 'general') => api.get('/show-news-script/', { category }),

    getAllNews: (category = '', search = '') => {
        const params = {};
        if (category) params.category = category;
        if (search) params.search = search;
        return api.get('/show-news/', { params });
    },

    askGemini: (question) => api.post('/ask-gemini/', { question }),

    textToSpeechById: (newsId) =>
        api.get(`/tts/${newsId}/`, { responseType: 'blob' }),

    /*** Generate avatar video for specific news article*/
    generateVideoById: (newsId) => api.post(`/avatar/${newsId}/`),

    /*** Check if video exists and get video status*/
    checkVideoExists: (newsId) => api.get(`/check-video/${newsId}/`),

    /*** Get video URL for playing - FIXED*/
    getVideoUrl: (newsId) => `${API_BASE_URL}/news_videos/${newsId}.mp4`,
};

export default api;