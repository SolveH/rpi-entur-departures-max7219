import os

import requests
from dotenv import load_dotenv

load_dotenv()

ET_CLIENT_NAME = os.environ["ET_CLIENT_NAME"]
JOURNEY_PLANNER_API_URL = "https://api.entur.io/journey-planner/v3/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "ET-Client-Name": ET_CLIENT_NAME
}

def call_journey_planner_api(query: str) -> dict:
    response = requests.post(JOURNEY_PLANNER_API_URL, json={"query": query}, headers=HEADERS)
    return response.json()

def get_estimated_calls_for_quay(quay_id: str) -> list:
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
    data = call_journey_planner_api(query)

    return data["data"]["quay"]["estimatedCalls"]

def get_stop_place_quays(stop_place_id: str) -> dict:
    time_range = 1800
    number_of_departures = 10
    query = """
    {
      stopPlace(id: "%s") {
        id
        name
        quays {
          id
          name
          estimatedCalls(timeRange: %s, numberOfDepartures: %s) {
            realtime
            aimedDepartureTime
            expectedDepartureTime
            destinationDisplay {
              frontText
            }
            serviceJourney {
              line {
                id
                publicCode
              }
            }
          }
        }
      }
    }
    """ % (stop_place_id, time_range, number_of_departures)
    data = call_journey_planner_api(query)
    return data["data"]["stopPlace"]["quays"]
