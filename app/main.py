import datetime
import sys
import time

import requests

STOP_PLACE_ID_SINSEN_T = "NSR:StopPlace:61268"

QUAY_ID_SINSEN_T_DIRECTION_SOUTH = "NSR:Quay:11078"


def get_estimated_calls(quay_id: str) -> list:
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


def filter_relevant_departures(expected_departures: list, service_journey_line_public_code: str) -> list:
    filtered_departures: list[dict] = [
        departure for departure in expected_departures
        if departure["serviceJourney"]["line"]["publicCode"] == service_journey_line_public_code
    ]
    return filtered_departures


def get_minutes_until_departure(departure: dict) -> int:
    target_time = datetime.datetime.fromisoformat(departure["expectedDepartureTime"])
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = target_time.astimezone(datetime.timezone.utc) - now
    minutes_until = int(delta.total_seconds() // 60)
    return minutes_until


def display_text_on_target_device(text, width=30, delay=0.1, repeat=2):
    padded = " " * width + text + " " * width
    for _ in range(repeat * len(text)):
        for i in range(len(text) + width):
            sys.stdout.write('\r' + padded[i:i + width])
            sys.stdout.flush()
            time.sleep(delay)
    print()  # Move to next line after done


if __name__ == "__main__":
    expected_departures_for_quay = get_estimated_calls(QUAY_ID_SINSEN_T_DIRECTION_SOUTH)
    relevant_departures = filter_relevant_departures(expected_departures_for_quay, "5")

    next_departure = relevant_departures[0]
    minutes_until_next_departure = get_minutes_until_departure(next_departure)

    departure_name = next_departure["serviceJourney"]["line"]["publicCode"] + " " + \
                     next_departure["destinationDisplay"]["frontText"]
    display_text_next_departure = departure_name + " " + str(minutes_until_next_departure) + " min"

    display_text_on_target_device(display_text_next_departure, width=40, delay=0.07)
