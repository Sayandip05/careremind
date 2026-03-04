class RateLimiter {
    constructor(maxRequests = 20) {
        this.maxRequests = maxRequests;
        this.requests = [];
    }
    
    canSend() {
        const now = Date.now();
        this.requests = this.requests.filter(t => now - t < 60000);
        return this.requests.length < this.maxRequests;
    }
    
    recordRequest() {
        this.requests.push(Date.now());
    }
}

module.exports = RateLimiter;
