# Authopie - A small scale, performant, authentification service, written with FastAPI

## Deployment

1. PULL
```
docker pull ghcr.io/klaemsch/authopie:latest
```
2. RUN
```
docker run --network ptv -d --restart unless-stopped --name ptv-auth -p 5555:5555 -v /path-to-config/config.json:/authopie/config.json ghcr.io/klaemsch/authopie:latest
```

## Useful Links

for cookies
- https://github.com/tiangolo/fastapi/issues/480

publish package
- https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry

jwt/jws/jwks
- https://datatracker.ietf.org/doc/html/rfc7517
- https://auth0.com/docs/secure/tokens/json-web-tokens/json-web-key-set-properties
- https://jwt.io/#debugger-io
- https://pyjwt.readthedocs.io/en/stable/usage.html#retrieve-rsa-signing-keys-from-a-jwks-endpoint

certs
- https://www.geocerts.com/certificate-decoder
- https://certificatetools.com/