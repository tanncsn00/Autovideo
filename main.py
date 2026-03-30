import argparse
import os

import uvicorn
from loguru import logger

from app.config import config


def main():
    parser = argparse.ArgumentParser(description="MoneyPrinterTurbo")
    parser.add_argument("--port", type=int, default=config.listen_port)
    parser.add_argument("--host", type=str, default=config.listen_host)
    parser.add_argument("--mode", choices=["api", "desktop"], default="api")
    parser.add_argument("--parent-pid", type=int, default=0)
    args = parser.parse_args()

    if args.mode == "desktop":
        os.environ["MPT_MODE"] = "desktop"
        os.environ["MPT_PORT"] = str(args.port)
        args.host = "127.0.0.1"
        logger.info(f"Desktop mode: port={args.port}, parent_pid={args.parent_pid}")

        if args.parent_pid:
            import threading
            def watchdog(ppid):
                try:
                    import psutil
                    while True:
                        if not psutil.pid_exists(ppid):
                            logger.warning("Parent process died, shutting down sidecar")
                            os._exit(0)
                        threading.Event().wait(5)
                except ImportError:
                    logger.warning("psutil not installed, watchdog disabled")
            threading.Thread(target=watchdog, args=(args.parent_pid,), daemon=True).start()

    logger.info(f"start server: http://{args.host}:{args.port}/docs")
    uvicorn.run(
        app="app.asgi:app",
        host=args.host,
        port=args.port,
        reload=config.reload_debug if args.mode == "api" else False,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
