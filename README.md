# tyjeski.com

Andres Tyjeski's personal web site

# Setup

Build and run Docker container locally using
```
docker build \ 
-t tyjeski .

docker run -it \
--name tyjeski \
-e "PORT=8765" \
-e "DEBUG=1" \
-p 8007:8765 \
tyjeski
```