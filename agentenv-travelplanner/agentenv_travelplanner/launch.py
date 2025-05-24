"""
TravelPlanner Environment Launch Script
"""

import argparse
import uvicorn
import logging

logger = logging.getLogger(__name__)


def launch():
    """启动 TravelPlanner 环境服务器的入口点"""
    
    parser = argparse.ArgumentParser(
        description="Launch TravelPlanner Environment Server for AgentGym"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level (default: info)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info(f"Starting TravelPlanner Environment Server...")
    logger.info(f"Host: {args.host}, Port: {args.port}")
    logger.info(f"Workers: {args.workers}, Log Level: {args.log_level}")
    
    try:
        # 启动服务器
        uvicorn.run(
            "agentenv_travelplanner.server:app",
            host=args.host,
            port=args.port,
            workers=args.workers if not args.reload else 1,
            log_level=args.log_level,
            reload=args.reload
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    launch() 