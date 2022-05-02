# Authopie - A small scale, performant, authentification service, written with FastAPI

## Deployment

1. BUILD
```
docker build https://github.com/klaemsch/authopie.git#main:backend -t klaemsch/authopie:v0.0.1 -t klaemsch/authopie:latest
```
2. RUN
```
docker run --network ptv -d --restart unless-stopped --name ptv-auth -p 5555:5555 -v /path-to-config/config.json:/authopie/config.json klaemsch/authopie
```