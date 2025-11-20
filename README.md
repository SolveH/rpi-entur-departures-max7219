# rpi-entur-departures-max7219

A script/application for displaying realtime departure times from Entur on a MAX7219 LED dot matrix display connected
to a Raspberry Pi (I use a Pi Zero W). It is configured to display the departure times for `5 Sognsvann via Tøyen` from
`Sinsen T`, but can easily be changed to display any other route by changing the constants in `rutetider.py`.

The project uses the [Luma_LED-Matrix library](https://luma-led-matrix.readthedocs.io/en/latest/intro.html) to display
text on the MAX7219 display.

# Prerequisites

- SPI needs to be enabled on the Raspberry Pi.
    - Enable SPI on the Raspberry Pi: `sudo raspi-config` -> `Interface Options -> `I4 SPI` -> `Yes`
- Install relevant APT packages by following instructions
  on [Luma_LED-Matrix installation](https://luma-led-matrix.readthedocs.io/en/latest/install.html)

# Local development setup

1. Make a copy of `.env.template` and replace placeholders with relevant values.
2. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
4. Set the `ET_CLIENT_NAME` environment variable:
    ```bash
    export ET_CLIENT_NAME=your_client_name
   ```
5. Run the application with
    ```bash
    python main.py start
    ```
6. Stop the application with
    ```bash
    python main.py stop
    ```
