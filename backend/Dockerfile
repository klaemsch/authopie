# load python base image
FROM python:latest

# we will work in /code from now on
WORKDIR /authopie

# copy requirements into container
COPY ./requirements.txt /authopie/requirements.txt

# install requirements inside container, upgrade if already installed
RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r /authopie/requirements.txt

# expose port 8000
EXPOSE 8000

# start uvicorn to host server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
