# Documentation of Backend APIs

Note that this document uses pretty-printed JSON for readability,
but you should not rely on that, nor is it necessary for request
payloads to be pretty-printed.

## POST `/v1/add`

Records a new set of career tasks. Expects a JSON payload like this:

    {
      "token": "abc (your token here)",
      "station": "Spirit of New York City, YZ Ceti system",
      "career": "Technologist",
      "rank": "Shipwright",
      "tasks": {
        "Run multiple salvage operations.": "174.00",
        "Market your salvage to Freebooters": "196.00",
        "Expand your business further.": "189.00",
        "Hire a bigger crew.": "189.00",
        "Hire even more illegal employees": "225.00"
      }
    }

In case of success, it returns a payload like this:

    {
        "character": "moritz",
        "factor": 1.0,
        "recorded": true
    }

If an error occurs, the error message is a property called `message`:

    {
        "message": "invalid token",
        "recorded": false
    }

## GET `/v1/stations`

Returns a list of stations that tasks bonuses have been recorded for.

[Observe it in the wild](https://ctt.tauguide.de/v1/stations).

Example response:

    {
      "data": [
        "Asimov Freehold, YZ Ceti system",
        "Cape Verde Stronghold, YZ Ceti system",
        "København, Sol system",
        "Nouveau Limoges, Sol system",
        "Paris Spatiale, Alpha Centauri system",
        "Spirit of New York City, YZ Ceti system",
        "Taungoo Station, Sol system",
        "Tau Station, Sol system",
        "Yards of Gadani, Alpha Centauri system"
        "YZ Ceti Jump Gate, YZ Ceti system",
      ]
    }


## GET `/v1/stats-by-character`

Returns an object of character names and their submission counts (under `data`):

[Observe it in the wild](https://ctt.tauguide.de/v1/stats-by-character).

    {
      "data": {
        "character1": 7,
        "character2": 9
      }
    }

## GET `/v1/station-needs-update/<station>`

Returns, for a given station (URL-encoded in the URL), whether an update would make sense.

[Observe it in the wild](https://ctt.tauguide.de/v1/station-needs-update/Spirit%20of%20New%20York%20City%2C%20YZ%20Ceti%20system).

It returns `{"needs_update": true}` if data for this station has been submitted in the last 6 hours, and `{"needs_update": false}` otherwise.
