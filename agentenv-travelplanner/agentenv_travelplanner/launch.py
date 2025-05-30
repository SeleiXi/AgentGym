"""
TravelPlanner Environment Launch Script
"""

import argparse
import uvicorn
import logging

logger = logging.getLogger(__name__)


def launch():
    """Entry point for launching TravelPlanner environment server"""
    
    parser = argparse.ArgumentParser(
        description="Launch TravelPlanner Environment Server for AgentGym"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=59399,
        help="Port to bind the server to (default: 59399)"
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
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info(f"Starting TravelPlanner Environment Server...")
    logger.info(f"Host: {args.host}, Port: {args.port}")
    logger.info(f"Workers: {args.workers}, Log Level: {args.log_level}")
    
    try:
        # Start server
        uvicorn.run(
            "server:app",
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