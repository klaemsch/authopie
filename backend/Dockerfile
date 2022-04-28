# load python base image
FROM python:latest

# we will work in /code from now on
WORKDIR /authopie

# copy backend files into container
COPY ./ /authopie/

# install requirements inside container, upgrade if already installed
RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r /authopie/requirements.txt

# expose port 5555
EXPOSE 5555

# start uvicorn to host server
CMD ["python", "start.py"]
