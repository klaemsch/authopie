Deployment

- docker build https://github.com/klaemsch/authopie.git#main:backend -t klaemsch/authopie:v0.0.1 -t klaemsch/authopie:latest
- docker run --network ptv -d --restart unless-stopped --name ptv-auth -p 5555:5555 klaemsch/authopie