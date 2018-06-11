# Xero extractor
Is registered as partner app (public app only lasts for ~30 minutes then needs reauthorization) https://developer.xero.com/documentation/auth-and-limits/public-applications

credentials required for reauthorization are stored in statefile (newly supports encryption).




# Configuration
```javascript
{
  "debug": true,
}
```
# Development
## Run locally
```
$ docker-compose run --rm dev
# gets you an interactive shell
# mounts the ./data/ folder to /data/
```

## Run tests
```
make test
# after dev session is finished to clean up containers..
make clean 
```
