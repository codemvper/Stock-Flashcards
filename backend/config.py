# -*- coding: utf-8 -*-
"""
配置文件
"""
import os

class Config:
    """基础配置"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Tushare配置
    TUSHARE_TOKEN = os.environ.get('TUSHARE_TOKEN') or '36a2f0e1e23c2bab7ae3b70572db4b6e87157831c7b5a3d1cf8efe24'
    
    # 缓存配置
    CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
    CACHE_TTL_HOURS = 24  # 缓存时间（小时）
    
    # API配置
    API_RETRY_TIMES = 3  # API调用重试次数
    API_TIMEOUT = 30  # API调用超时时间（秒）
    
    # 数据配置
    MAX_HISTORY_YEARS = 5  # 历史数据年限
    MIN_MARKET_VALUE = 10  # 最小市值筛选（亿元）


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境应该从环境变量读取敏感信息
    SECRET_KEY = os.environ.get('SECRET_KEY')
    TUSHARE_TOKEN = os.environ.get('TUSHARE_TOKEN')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

