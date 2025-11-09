# rutetider

Lite prosjekt for å hente rutetider for ei ønska rute (per no `5 Sognsvann via Tøyen` frå `Sinsen T`) og vise kor lang
tid det er til neste avgang på en Raspberry Pi Zero med eit LED dot matrix display. 

# Local development setup

1. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the application with
    ```bash
    python app/main.py
    ```
