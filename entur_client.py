import requests


def get_estimated_calls_for_quay(quay_id: str) -> list:
    url = "https://api.entur.io/journey-planner/v3/graphql"
    headers = {
        "Content-Type": "application/json",
        "ET-Client-Name": "hunvik_com-hobbyproject"
    }
    timeRange = 1000
    numberOfDepartures = 5
    query = """
    {
      quay(id: "%s") {
        id
        name
        estimatedCalls(timeRange: %s, numberOfDepartures: %s) {
          realtime
          expectedDepartureTime
          destinationDisplay {
            frontText
          }
          serviceJourney {
            line {
              publicCode
            }
          }
        }
      }
    }
    """ % (quay_id, timeRange, numberOfDepartures)
    response = requests.post(url, json={"query": query}, headers=headers)
    data = response.json()
    expected_departures = data["data"]["quay"]["estimatedCalls"]

    return expected_departures
