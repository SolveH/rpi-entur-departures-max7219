import requests


def get_estimated_calls_for_quay(quay_id: str) -> list:
    url = "https://api.entur.io/journey-planner/v3/graphql"
    headers = {
        "Content-Type": "application/json",
        "ET-Client-Name": "hunvik_com-hobbyproject"
    }
    query = """
    {
      quay(id: "%s") {
        id
        name
        estimatedCalls(timeRange: 7200, numberOfDepartures: 5) {
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
    """ % quay_id
    response = requests.post(url, json={"query": query}, headers=headers)
    data = response.json()
    expected_departures = data["data"]["quay"]["estimatedCalls"]

    return expected_departures
