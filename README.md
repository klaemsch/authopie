# Authopie - A small scale, performant, authentification and authorization service, written with FastAPI

# Advantages
- simple
- small scale
- single application
- runs out of the box (no db needed)

# Features
- user/role management
- JWT with RSA private/public key signature
- jwks endpoint for client-side verification
- password hashing with bcrypt
- api key generation
- permission management with scopes

# Structure

## Routers
- ``user.py``: GET user, POST user, PUT user, DELETE user
- ``role.py``: GET role, POST role, DELETE role
- ``token.py``: generate and renew token pair (access_token/refresh_token), generate api token (JWT)
- ``jwks.py``: provides endpoint (``/.well-known/jwks.json``) for jwks retrieval
- ``import_export.py``: export users/roles from db to json, import users/roles from json to db

## crud
- ``key_pairs.py``: create new key pairs (private/public) in db, get key pairs from db
- ``role.py``: create, delete and get roles from/in db
- ``user.py``: create, delete, update and get roles from/in db

## util
utils are methods, models or classes used by authopie to make life simpler, like logging, loading configs from file, or setting cookies to a response
- ``auth.py``: create tokens, validate tokens, authorize and authenticate user via token
- ``constants.py``: Scopes for authorizing tokens/users (permission management) TODO??
- ``pwdhash.py``: hash password, compare password to hash from db
- ``config.py``: load config from file
- ``logger.py``: get and test custom logger
- ``cookie.py``: set cookies in response to client

## dependencies
dependencies are methods, models or classes, that endpoints to depend on, fastapi loads them with the request
- ``database.py``: SQLAlchemy configuration, Mixin for creating database elements, get connection to database
- ``security.py``: login/refresh form classes + oauth2 integration for swagger (exports JWT from cookie)

# Deployment

1. PULL
```
docker pull ghcr.io/klaemsch/authopie:latest
```
2. RUN
```
docker run --network ptv -d --restart unless-stopped --name ptv-auth -p 5555:5555 -v /path-to-config/config.json:/authopie/config.json ghcr.io/klaemsch/authopie:latest
```

# Publishing image to ghcr
- Generate Token: https://github.com/settings/tokens/new?scopes=write:packages
```
docker build . -t ghcr.io/klaemsch/authopie:latest -t ghcr.io/klaemsch/authopie:v0.2
export CR_PAT=TOKEN
echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
docker push --all-tags ghcr.io/klaemsch/authopie
```

# Useful Links

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