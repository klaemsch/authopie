import uvicorn

# load config from __init__.py in src
from .src import config


def main():

    uvicorn.run(
        "authopie.src.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level='debug',
        proxy_headers=True,
        forwarded_allow_ips="*"
    )


if __name__ == "__main__":
    main()
