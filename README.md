# Xero extractor
Is registered as partner app (public app only lasts for ~30 minutes then needs reauthorization) https://developer.xero.com/documentation/auth-and-limits/public-applications

credentials required for reauthorization are stored in statefile (newly supports encryption).




# Configuration
```javascript
{
  "debug": true,
  "endpoints": [
    {
      "endpoint": "Contacts",
      "parameters": {"IncludeArchived": true}
    },
    {
      "endpoint": "Contacts",
      "parameters": {"since": "2 days ago UTC"}
    },
    {
      "endpoint": "Journals"
    }
  ]
}
```

The `"endpoints"` is a list of endpoint configurations. Each configuration has an `"endpoint"` defined, with optional `parameters` (see the api [documentation](https://developer.xero.com/documentation/api/api-overview) for each endpoint)

```javascript
{
  "endpoint": "Name of endpoint",
  "parameters": {
    "literal": "parameters as seen in the api documentation",
    "since": "a special filter - see below"
  }
}
```

The `since` parameter is used to set the `if-modified-since` header and should be in UTC. Example values are `2 days ago UTC` or `2018-01-31 12:00:00 UTC`


TODO:
use `client.<endpoint>.filter(page=1..N, **extra_params)`
for all endpoints (instead of `client.<endpoint>.all()`)
and count # of requests in a 60 seconds window



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
