# Xero extractor

# Configuration
```javascript
{
  "debug": true,
  "action": "extract",
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
    },
    {
          "endpoint": "Accounts",
          "parameters": ""
    }
  ]
}
```

The `"endpoints"` is a list of endpoint configurations. Each configuration has an `"endpoint"` defined, with optional `parameters` (see the api [documentation](https://developer.xero.com/documentation/api/api-overview) for each endpoint)

```javascript
{
  "endpoint": "Name of endpoint",
  "parameters": {
    "parameter_A": "as seen in the api documentation",
    "since": "a special filter - see below"
  }
}
```

The `since` parameter is used to set the `if-modified-since` header and should be in UTC. Example values are `2 days ago UTC` or `2018-01-31 12:00:00 UTC`


The extractor outputs json objects in csv by default. You might be interested in serializing this into pure csv using [flatten-json](https://components.keboola.com/~/components/apac.processor-flatten-json) processor

```javascript
{
  "before": [],
  "after": [
    {
      "definition": {
        "component": "apac.processor-flatten-json"
      }
    }
  ]
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
cp .env_template .env
# edit .env to add the required env variables with credentials
make test
# or make testk what='test_validating_' #if you want to run just certain tests whose name match `test_validating_`
# after dev session is finished to clean up containers..
make clean 
```
