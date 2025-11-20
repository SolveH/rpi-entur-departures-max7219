import atexit
import datetime
import os
import signal
import sys
import threading
import time

import RPi.GPIO as GPIO
from PIL import ImageFont
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219

from entur_client import get_estimated_calls_for_quay

STOP_PLACE_ID_SINSEN_T = "NSR:StopPlace:61268"
QUAY_ID_SINSEN_T_SUBWAY_DIRECTION_SOUTH = "NSR:Quay:11078"
RINGEN_VIA_STORO_SUBWAY_CODE = "5"

cache = {
    QUAY_ID_SINSEN_T_SUBWAY_DIRECTION_SOUTH: [],
}


def cache_updater(quay_id: str):
    while True:
        cache[QUAY_ID_SINSEN_T_SUBWAY_DIRECTION_SOUTH] = get_estimated_calls_for_quay(quay_id)
        time.sleep(60)


def get_relevant_departures() -> list:
    estimated_calls = cache[QUAY_ID_SINSEN_T_SUBWAY_DIRECTION_SOUTH]
    return filter_relevant_departures(estimated_calls, RINGEN_VIA_STORO_SUBWAY_CODE)


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


def get_next_departures_display_text(relevant_departures: list) -> str:
    if len(relevant_departures) >= 2:
        next_departure = relevant_departures[0]
        second_next_departure = relevant_departures[1]

        departure_name = next_departure["serviceJourney"]["line"]["publicCode"] + " " + \
                         next_departure["destinationDisplay"]["frontText"]

        minutes_until_next_departure = get_minutes_until_departure(next_departure)
        minutes_until_second_next_departure = get_minutes_until_departure(second_next_departure)
        return (departure_name + " " + str(minutes_until_next_departure) +
                " og " + str(minutes_until_second_next_departure) + " min")
    elif len(relevant_departures) == 1:
        next_departure = relevant_departures[0]
        departure_name = next_departure["serviceJourney"]["line"]["publicCode"] + " " + \
                         next_departure["destinationDisplay"]["frontText"]
        minutes_until_next_departure = get_minutes_until_departure(next_departure)
        return departure_name + " " + str(minutes_until_next_departure) + " min"
    else:
        return "Ingen rutetider tilgjengelig"


def get_font() -> ImageFont:
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "code2000.ttf")
    return ImageFont.truetype(font_path, 8)


def display_next_departures_on_max7219():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, width=32, height=8, block_orientation=-90)
    device.contrast(3)
    virtual = viewport(device, width=32, height=16)

    def cleanup():
        device.clear()
        GPIO.cleanup()

    atexit.register(cleanup)

    def handle_sigterm(signum, frame):
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_sigterm)

    threading.Thread(target=cache_updater, args=(QUAY_ID_SINSEN_T_SUBWAY_DIRECTION_SOUTH,), daemon=True).start()
    # TODO: fikse hardkoda url
    font = get_font()

    time.sleep(5)  # sleep some seconds to ensure cache is populated with first entry

    last_text = ""
    text = ""
    text_width = 0
    display_width = device.width
    offset = 0
    while True:
        relevant_departures = get_relevant_departures()
        new_text = get_next_departures_display_text(relevant_departures)

        # Only update text and width if the text has changed to avoid stutter
        if new_text != last_text:
            text = new_text
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            last_text = new_text

        scroll_offset = offset % (text_width + display_width)

        with canvas(device) as draw:
            draw.text((-scroll_offset + display_width, -1), text, fill="white", font=font)
        time.sleep(0.01)
        offset = (offset + 1) % 1_000_000
