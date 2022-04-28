import uvicorn

from src.config import config


def main():

    uvicorn.run(
        "src.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level=config.LOG_LEVEL,
        proxy_headers=True
    )


if __name__ == "__main__":
    main()
