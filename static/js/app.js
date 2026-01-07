// 全局应用配置
const AppConfig = {
    API_BASE: '/api/v1',
    PAGE_SIZE: 10,

    // 区域类型配置
    AREA_TYPES: {
        FOREST: '森林',
        GRASSLAND: '草地'
    },

    // 传感器类型配置
    SENSOR_TYPES: {
        TEMPERATURE: '温度',
        HUMIDITY: '湿度',
        IMAGE: '图像'
    },

    // 颜色配置
    COLORS: {
        PRIMARY: '#2E7D32',
        SECONDARY: '#4CAF50',
        WARNING: '#FF9800',
        DANGER: '#F44336',
        INFO: '#2196F3'
    }
};

// 工具函数
class Utils {
    static formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    }

    static formatNumber(num, decimals = 2) {
        if (num === null || num === undefined) return '-';
        return Number(num).toFixed(decimals);
    }

    static showToast(message, type = 'success') {
        // 简单的toast实现
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    static confirm(message) {
        return new Promise((resolve) => {
            const confirmed = window.confirm(message);
            resolve(confirmed);
        });
    }
}

// API客户端
class ApiClient {
    constructor(baseUrl = AppConfig.API_BASE) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }

    // 区域相关API
    getAreas(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/environment/areas?${query}`);
    }

    getArea(id) {
        return this.request(`/environment/areas/${id}`);
    }

    createArea(data) {
        return this.request('/environment/areas', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    updateArea(id, data) {
        return this.request(`/environment/areas/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    deleteArea(id) {
        return this.request(`/environment/areas/${id}`, {
            method: 'DELETE'
        });
    }

    // 传感器相关API
    getSensors(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/environment/sensors?${query}`);
    }

    getSensor(id) {
        return this.request(`/environment/sensors/${id}`);
    }

    createSensor(data) {
        return this.request('/environment/sensors', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    deleteSensor(id) {
        return this.request(`/environment/sensors/${id}`, {
            method: 'DELETE'
        });
    }

    // 监测数据相关API
    getMonitorData(sensorId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/environment/sensors/${sensorId}/monitors?${query}`);
    }

    getRecentMonitorData(sensorId, hours = 24, limit = 100) {
        return this.request(`/environment/sensors/${sensorId}/monitors/recent?hours=${hours}&limit=${limit}`);
    }

    createMonitorData(data) {
        return this.request('/environment/monitors', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    batchCreateMonitorData(dataList) {
        return this.request('/environment/monitors/batch', {
            method: 'POST',
            body: JSON.stringify(dataList)
        });
    }

    // 统计API
    getAreaStatistics() {
        return this.request('/environment/areas/statistics');
    }

    getSensorStatistics() {
        return this.request('/environment/sensors/statistics');
    }

    getAreaDashboard(areaId) {
        return this.request(`/environment/areas/${areaId}/dashboard`);
    }
}

// 初始化全局API客户端
window.api = new ApiClient();
window.utils = Utils;
window.config = AppConfig;