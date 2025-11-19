import datetime
import time
import threading

import RPi.GPIO as GPIO
import requests
from PIL import ImageFont
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219

STOP_PLACE_ID_SINSEN_T = "NSR:StopPlace:61268"

QUAY_ID_SINSEN_T_DIRECTION_SOUTH = "NSR:Quay:11078"

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, width=32, height=8, block_orientation=-90)
device.contrast(3)
virtual = viewport(device, width=32, height=16)

cache = {
    "data": [],
    "timestamp": 0
}


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


def cache_updater(quay_id: str):
    while True:
        cache["data"] = get_estimated_calls(quay_id)
        cache["timestamp"] = time.time()
        print("Updated cache (background)")
        time.sleep(60)


def get_relevant_departures() -> list:
    estimated_calls = cache["data"]
    return filter_relevant_departures(estimated_calls, "5")


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


if __name__ == "__main__":
    threading.Thread(target=cache_updater, args=(QUAY_ID_SINSEN_T_DIRECTION_SOUTH,), daemon=True).start()
    font = ImageFont.truetype("/home/solveh/code/rutetider/fonts/code2000.ttf", 8)

    time.sleep(5) # sleep some seconds to ensure cache is populated with first entry

    try:
        offset = 0
        while True:
            relevant_departures = get_relevant_departures()

            next_departure = relevant_departures[0]
            second_next_departure = relevant_departures[1]

            departure_name = next_departure["serviceJourney"]["line"]["publicCode"] + " " + \
                             next_departure["destinationDisplay"]["frontText"]
            # Recalculate minutes and text on every frame
            minutes_until_next_departure = get_minutes_until_departure(next_departure)
            minutes_until_second_next_departure = get_minutes_until_departure(second_next_departure)
            display_text_next_departure = (
                    departure_name + " " + str(minutes_until_next_departure) +
                    " og " + str(minutes_until_second_next_departure) + " min"
            )
            text = display_text_next_departure
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            display_width = device.width

            # Calculate current scroll position
            scroll_offset = offset % (text_width + display_width)

            with canvas(device) as draw:
                draw.text((-scroll_offset + display_width, -2), text, fill="white", font=font)
            time.sleep(0.01)
            if offset > 1_000_000:
                offset = 0
            else:
                offset += 1
    except KeyboardInterrupt:
        GPIO.cleanup()
