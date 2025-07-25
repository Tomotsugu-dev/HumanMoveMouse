"""
日志系统实现
提供统一的日志记录和错误处理机制
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Any
from functools import wraps
import traceback


class LoggerManager:
    """日志管理器"""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.log_dir = Path("logs")
            self.log_dir.mkdir(exist_ok=True)
            self.setup_root_logger()
    
    def setup_root_logger(self):
        """设置根日志记录器"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # 清除现有的处理器
        root_logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # 文件处理器
        log_file = self.log_dir / f"mouse_trajectory_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取或创建指定名称的日志记录器"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        
        return self._loggers[name]


# 全局日志管理器实例
logger_manager = LoggerManager()


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器的便捷函数"""
    return logger_manager.get_logger(name)


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or get_logger("ErrorHandler")
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """处理错误并记录"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # 构建错误信息
        log_msg = f"Error in {context}: {error_type} - {error_msg}"
        
        # 记录完整的堆栈跟踪
        self.logger.error(log_msg, exc_info=True)
        
        # 根据错误类型决定是否需要特殊处理
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            # 允许这些异常继续传播
            raise
        elif isinstance(error, MemoryError):
            # 内存错误需要特殊处理
            self.logger.critical("Memory error occurred, attempting cleanup...")
            # 这里可以添加清理逻辑
    
    def log_warning(self, message: str, context: str = "") -> None:
        """记录警告信息"""
        log_msg = f"Warning in {context}: {message}" if context else f"Warning: {message}"
        self.logger.warning(log_msg)


def error_handler(context: str = "", reraise: bool = True):
    """
    错误处理装饰器
    
    Args:
        context: 错误上下文描述
        reraise: 是否重新抛出异常
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            handler = ErrorHandler(logger)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler.handle_error(e, context or f"{func.__module__}.{func.__name__}")
                if reraise:
                    raise
                return None
        
        return wrapper
    return decorator


def log_performance(func):
    """性能日志装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        logger.debug(f"{func.__name__} executed in {duration:.3f} seconds")
        
        return result
    
    return wrapper


class PerformanceLogger:
    """性能日志记录器，用于记录代码块的执行时间"""
    
    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        self.name = name
        self.logger = logger or get_logger("Performance")
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            self.logger.debug(f"{self.name} completed in {duration:.3f} seconds")
        
        return False  # 不抑制异常