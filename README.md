# Xero extractor
Is registered as partner app (public app only lasts for ~30 minutes then needs reauthorization) https://developer.xero.com/documentation/auth-and-limits/public-applications

credentials required for reauthorization are stored in statefile (newly supports encryption).




# Configuration
## Authorization
Authorization is *temporary* slightly more complicated. Until support for OAuth-1.0a RSA signed requests is added to [OAuth-bundle](https://github.com/keboola/oauth-v2-bundle/issues/38)

### Get authoriazation url
Run the extractor with the following config

```javascript
{
  "action": "get_authorization_url"
}
```
This will print the XERO authorization url in the job logs. Go and visit the url and authorize your account. You will be given a 6 digits verification code

Run the extractor with the following config.

```javascript
{
  "action": "verify",
  "verification_code" : "<YOUR_CODE_FROM_PREVIOUS_STEP_HERE>"
}
```

This will securely save the credentials and the extractor is ready to be used:
## Actual extraction
```javascript
{
  "debug": true,
  "action": "extract"
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
cp .env_template .env
# edit .env to add the required env variables with credentials
make test
# or make testk what='test_validating_' #if you want to run just certain tests whose name match `test_validating_`
# after dev session is finished to clean up containers..
make clean 
```

## In keboola components
pass the ([encrypted](https://keboolaencryption.docs.apiary.io/#reference/encrypt/encryption/encrypt-data)) `#consumer_secret` and `#consumer_key` through stack_parameters
