/**
 * 飞书API限流管理器
 * 避免触发API限流，提供重试机制
 */

class RateLimiter {
  constructor(options = {}) {
    // 配置参数
    this.maxRequestsPerMinute = options.maxRequestsPerMinute || 30; // 每分钟最大请求数
    this.minIntervalMs = options.minIntervalMs || 2000; // 最小间隔时间（毫秒）
    this.maxRetryTimes = options.maxRetryTimes || 3; // 最大重试次数
    this.retryDelayMs = options.retryDelayMs || 5000; // 重试延迟（毫秒）
    
    // 状态追踪
    this.requestQueue = [];
    this.isProcessing = false;
    this.lastRequestTime = 0;
    this.requestCount = 0; // 当前分钟内的请求计数
    this.minuteStartTime = Date.now();
  }
  
  /**
   * 添加请求到队列
   * @param {Function} requestFn - 请求函数
   * @param {Object} options - 请求选项
   * @returns {Promise} 请求结果
   */
  async enqueue(requestFn, options = {}) {
    const {
      priority = 0, // 优先级，数字越小优先级越高
      retryable = true, // 是否可重试
      context = null, // 上下文信息，用于日志
    } = options;
    
    return new Promise((resolve, reject) => {
      this.requestQueue.push({
        requestFn,
        priority,
        retryable,
        context,
        resolve,
        reject
      });
      
      // 按优先级排序
      this.requestQueue.sort((a, b) => a.priority - b.priority);
      
      // 开始处理队列
      this.processQueue();
    });
  }
  
  /**
   * 处理请求队列
   */
  async processQueue() {
    if (this.isProcessing || this.requestQueue.length === 0) {
      return;
    }
    
    this.isProcessing = true;
    
    try {
      while (this.requestQueue.length > 0) {
        // 检查限流
        if (!this.canMakeRequest()) {
          await this.waitUntilAllowed();
        }
        
        const request = this.requestQueue.shift();
        
        try {
          const result = await this.executeWithRetry(request);
          request.resolve(result);
        } catch (error) {
          if (request.retryable && this.canRetry(error)) {
            // 重新加入队列，降低优先级
            request.priority += 10;
            this.requestQueue.push(request);
          } else {
            request.reject(error);
          }
        }
      }
    } catch (error) {
      console.error('[RateLimiter] 队列处理错误:', error);
    } finally {
      this.isProcessing = false;
    }
  }
  
  /**
   * 执行带重试的请求
   */
  async executeWithRetry(request) {
    let lastError;
    
    for (let attempt = 0; attempt <= this.maxRetryTimes; attempt++) {
      try {
        if (attempt > 0) {
          const delay = this.retryDelayMs * Math.pow(2, attempt - 1); // 指数退避
          console.log(`[RateLimiter] 重试第 ${attempt} 次，延迟 ${delay}ms`);
          await this.sleep(delay);
        }
        
        const result = await request.requestFn();
        
        // 成功，重置请求计数
        this.recordSuccess();
        return result;
        
      } catch (error) {
        lastError = error;
        
        // 检查是否是限流错误
        if (this.isRateLimitError(error) && attempt < this.maxRetryTimes) {
          console.log(`[RateLimiter] 触发限流，将重试...`);
          continue;
        }
        
        // 其他错误，不重试
        if (attempt > 0) {
          console.warn(`[RateLimiter] 请求失败:`, error);
        }
        throw error;
      }
    }
    
    throw lastError;
  }
  
  /**
   * 检查是否可以发起新请求
   */
  canMakeRequest() {
    const now = Date.now();
    
    // 检查最小间隔
    if (now - this.lastRequestTime < this.minIntervalMs) {
      return false;
    }
    
    // 检查每分钟请求数
    this.resetCountIfNeeded(now);
    if (this.requestCount >= this.maxRequestsPerMinute) {
      return false;
    }
    
    return true;
  }
  
  /**
   * 记录成功请求
   */
  recordSuccess() {
    const now = Date.now();
    this.lastRequestTime = now;
    this.resetCountIfNeeded(now);
    this.requestCount++;
  }
  
  /**
   * 重置计数器（如果需要）
   */
  resetCountIfNeeded(now = Date.now()) {
    if (now - this.minuteStartTime >= 60000) {
      this.minuteStartTime = now;
      this.requestCount = 0;
    }
  }
  
  /**
   * 等待直到允许请求
   */
  async waitUntilAllowed() {
    while (!this.canMakeRequest()) {
      const now = Date.now();
      this.resetCountIfNeeded(now);
      
      if (this.requestCount >= this.maxRequestsPerMinute) {
        // 等待到下一分钟
        const waitTime = 60000 - (now - this.minuteStartTime);
        console.log(`[RateLimiter] 每分钟请求已达上限，等待 ${waitTime}ms`);
        await this.sleep(waitTime);
      } else if (this.lastRequestTime > 0) {
        // 等待最小间隔
        const waitTime = this.minIntervalMs - (now - this.lastRequestTime);
        await this.sleep(Math.max(0, waitTime));
      }
    }
  }
  
  /**
   * 判断是否是限流错误
   */
  isRateLimitError(error) {
    if (!error) return false;
    
    const errorStr = String(error);
    const rateLimitKeywords = [
      '限流',
      'rate limit',
      '429',
      'Too Many Requests',
      '请求过于频繁',
      'request id',
      '触发限流',
      '超出调用限制',
      '超出配额',
      'exceeded quota',
      'throttle'
    ];
    
    return rateLimitKeywords.some(keyword => 
      errorStr.toLowerCase().includes(keyword)
    );
  }
  
  /**
   * 判断是否可以重试
   */
  canRetry(error) {
    // 网络错误可重试
    const networkErrors = [
      'ECONNRESET',
      'ETIMEDOUT',
      'ENOTFOUND',
      'ECONNREFUSED'
    ];
    
    // 限流错误可重试
    if (this.isRateLimitError(error)) {
      return true;
    }
    
    const errorStr = String(error);
    return networkErrors.some(err => errorStr.includes(err));
  }
  
  /**
   * 延迟函数
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  /**
   * 获取当前状态
   */
  getStatus() {
    return {
      queueLength: this.requestQueue.length,
      isProcessing: this.isProcessing,
      requestCount: this.requestCount,
      maxRequestsPerMinute: this.maxRequestsPerMinute,
      timeUntilNextMinute: 60000 - (Date.now() - this.minuteStartTime),
      timeSinceLastRequest: Date.now() - this.lastRequestTime
    };
  }
}

// 创建全局单例
const globalRateLimiter = new RateLimiter({
  maxRequestsPerMinute: 30,
  minIntervalMs: 2000,
  maxRetryTimes: 3,
  retryDelayMs: 5000
});

// 导出
module.exports = {
  RateLimiter,
  globalRateLimiter
};
