import os

import requests
from dotenv import load_dotenv

load_dotenv()

ET_CLIENT_NAME = os.environ["ET_CLIENT_NAME"]


def get_estimated_calls_for_quay(quay_id: str) -> list:
    url = "https://api.entur.io/journey-planner/v3/graphql"
    headers = {
        "Content-Type": "application/json",
        "ET-Client-Name": ET_CLIENT_NAME
    }
    time_range = 7200
    number_of_departures = 5
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
    """ % (quay_id, time_range, number_of_departures)
    response = requests.post(url, json={"query": query}, headers=headers)
    data = response.json()
    expected_departures = data["data"]["quay"]["estimatedCalls"]

    return expected_departures
