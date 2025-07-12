/**
 * Augment Data Intelligence SDK for JavaScript/Node.js
 * The easiest way to add industry-specific analytics to your app
 */

class AugmentAPI {
    constructor(apiKey, options = {}) {
        this.apiKey = apiKey;
        this.baseURL = options.baseURL || 'https://api.augment.com/v1';
        this.timeout = options.timeout || 30000;
        
        // Validate API key format
        if (!apiKey || !apiKey.startsWith('ak_')) {
            throw new Error('Invalid API key format. Expected: ak_[tier]_[secret]');
        }
    }

    /**
     * Analyze data with industry-specific intelligence
     * @param {Object} options - Analysis options
     * @param {Array|Object} options.data - Data to analyze (CSV, JSON, or file)
     * @param {string} options.industry - Industry type (automotive, retail, etc.)
     * @param {Array} options.insights - Types of insights to generate
     * @returns {Promise<Object>} Analysis results with AI insights
     */
    async analyze(options) {
        const { data, industry, insights = ['trends', 'correlations', 'recommendations'] } = options;
        
        const payload = {
            data: this._prepareData(data),
            industry,
            insight_types: insights,
            auto_detect_industry: !industry
        };

        return this._request('POST', '/data/analyze', payload);
    }

    /**
     * Create and execute a data pipeline
     * @param {Object} pipeline - Pipeline configuration
     * @returns {Promise<Object>} Pipeline execution results
     */
    async createPipeline(pipeline) {
        const response = await this._request('POST', '/pipelines/create', pipeline);
        
        // Auto-execute if requested
        if (pipeline.auto_execute) {
            return this.executePipeline(response.pipeline_id);
        }
        
        return response;
    }

    /**
     * Execute an existing pipeline
     * @param {string} pipelineId - Pipeline ID
     * @param {Object} options - Execution options
     * @returns {Promise<Object>} Execution results
     */
    async executePipeline(pipelineId, options = {}) {
        const payload = {
            wait_for_completion: options.wait !== false,
            timeout: options.timeout || 300
        };

        return this._request('POST', `/pipelines/${pipelineId}/execute`, payload);
    }

    /**
     * Get industry-specific templates
     * @param {string} industry - Industry name
     * @returns {Promise<Object>} Available templates
     */
    async getIndustryTemplates(industry) {
        return this._request('GET', `/industries/${industry}/templates`);
    }

    /**
     * Generate real-time insights from streaming data
     * @param {Object} options - Streaming options
     * @returns {WebSocket} WebSocket connection for real-time insights
     */
    streamInsights(options) {
        const wsUrl = this.baseURL.replace('https://', 'wss://') + '/insights/stream';
        const ws = new WebSocket(`${wsUrl}?api_key=${this.apiKey}`);
        
        ws.onopen = () => {
            ws.send(JSON.stringify(options));
        };
        
        return ws;
    }

    /**
     * Register a webhook for pipeline events
     * @param {Object} webhook - Webhook configuration
     * @returns {Promise<Object>} Webhook registration result
     */
    async registerWebhook(webhook) {
        return this._request('POST', '/webhooks/register', webhook);
    }

    /**
     * Upload and analyze a file
     * @param {File|Buffer} file - File to analyze
     * @param {Object} options - Analysis options
     * @returns {Promise<Object>} Analysis results
     */
    async analyzeFile(file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('options', JSON.stringify(options));

        return this._request('POST', '/data/upload-analyze', formData, {
            'Content-Type': 'multipart/form-data'
        });
    }

    /**
     * Get usage analytics for your API key
     * @param {Object} options - Analytics options
     * @returns {Promise<Object>} Usage statistics
     */
    async getUsageAnalytics(options = {}) {
        const params = new URLSearchParams(options);
        return this._request('GET', `/analytics/usage?${params}`);
    }

    // Private methods
    async _request(method, endpoint, data = null, customHeaders = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const headers = {
            'Authorization': `Bearer ${this.apiKey}`,
            'User-Agent': 'Augment-SDK-JS/1.0.0',
            ...customHeaders
        };

        if (data && !(data instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }

        const config = {
            method,
            headers,
            timeout: this.timeout
        };

        if (data) {
            config.body = data instanceof FormData ? data : JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new AugmentAPIError(
                    error.message || `HTTP ${response.status}`,
                    response.status,
                    error
                );
            }

            return await response.json();
        } catch (error) {
            if (error instanceof AugmentAPIError) {
                throw error;
            }
            throw new AugmentAPIError(`Network error: ${error.message}`, 0, error);
        }
    }

    _prepareData(data) {
        if (Array.isArray(data)) {
            return { format: 'json', content: data };
        } else if (typeof data === 'string') {
            // Assume CSV string
            return { format: 'csv', content: data };
        } else if (data instanceof File) {
            return { format: 'file', content: data };
        } else {
            return { format: 'json', content: data };
        }
    }
}

/**
 * Custom error class for API errors
 */
class AugmentAPIError extends Error {
    constructor(message, statusCode, details) {
        super(message);
        this.name = 'AugmentAPIError';
        this.statusCode = statusCode;
        this.details = details;
    }
}

/**
 * Helper functions for common use cases
 */
class AugmentHelpers {
    /**
     * Quick automotive dealership analysis
     */
    static async analyzeAutomotiveSales(apiKey, salesData) {
        const augment = new AugmentAPI(apiKey);
        return augment.analyze({
            data: salesData,
            industry: 'automotive',
            insights: ['sales_velocity', 'inventory_optimization', 'pricing_analysis']
        });
    }

    /**
     * Quick retail inventory analysis
     */
    static async analyzeRetailInventory(apiKey, inventoryData) {
        const augment = new AugmentAPI(apiKey);
        return augment.analyze({
            data: inventoryData,
            industry: 'retail',
            insights: ['demand_forecasting', 'stockout_prediction', 'category_performance']
        });
    }

    /**
     * Quick restaurant performance analysis
     */
    static async analyzeRestaurantPerformance(apiKey, orderData) {
        const augment = new AugmentAPI(apiKey);
        return augment.analyze({
            data: orderData,
            industry: 'restaurant',
            insights: ['menu_optimization', 'peak_hours', 'customer_preferences']
        });
    }

    /**
     * Quick fintech user behavior analysis
     */
    static async analyzeFintechUsers(apiKey, userData) {
        const augment = new AugmentAPI(apiKey);
        return augment.analyze({
            data: userData,
            industry: 'fintech',
            insights: ['user_engagement', 'churn_prediction', 'feature_adoption']
        });
    }
}

// Export for different environments
if (typeof module !== 'undefined' && module.exports) {
    // Node.js
    module.exports = { AugmentAPI, AugmentAPIError, AugmentHelpers };
} else if (typeof window !== 'undefined') {
    // Browser
    window.AugmentAPI = AugmentAPI;
    window.AugmentAPIError = AugmentAPIError;
    window.AugmentHelpers = AugmentHelpers;
}

/**
 * Usage Examples:
 * 
 * // Basic analysis
 * const augment = new AugmentAPI('ak_live_your_secret_key');
 * const insights = await augment.analyze({
 *   data: csvData,
 *   industry: 'automotive'
 * });
 * 
 * // Real-time streaming
 * const ws = augment.streamInsights({
 *   industry: 'fintech',
 *   events: ['transaction', 'user_action']
 * });
 * ws.onmessage = (event) => {
 *   const insight = JSON.parse(event.data);
 *   console.log('New insight:', insight);
 * };
 * 
 * // Quick helpers
 * const salesInsights = await AugmentHelpers.analyzeAutomotiveSales(
 *   'ak_live_your_key',
 *   salesData
 * );
 */
