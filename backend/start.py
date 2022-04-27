import uvicorn
import logging


def main():

    uvicorn.run(
        "src.main:app",
        host='127.0.0.1',
        port=5555,
        reload=True,
        log_level=logging.DEBUG,
    )


if __name__ == "__main__":
    main()
