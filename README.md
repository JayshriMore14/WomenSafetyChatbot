# AI-Powered Women's Safety Chatbot

This is a complete Python and Streamlit safety chatbot application. It uses offline, predefined intelligent responses and local Python libraries. It does not require OpenAI, Gemini, Claude, or any paid AI API.

## Features

1. Emergency SOS button with emergency mode, instructions, and simulated alerts.
2. Safety chatbot for night travel, cyber safety, public transport, self-defense, online harassment, and emotional support.
3. Nearby help centers with Folium map markers for police stations, hospitals, and women help centers.
4. Emergency contact add, edit, delete, and display system using SQLite.
5. Fake incoming call simulation with caller selection and emergency escape UI.
6. Voice input with SpeechRecognition and text-to-speech with pyttsx3.
7. Self-defense categorized guidance and quick action steps.
8. Mental support chat prompts and calming responses.
9. Danger keyword detection for words such as help, danger, unsafe, stalker, emergency, and trapped.
10. Live location sharing simulation with current location map and generated location message.

## Folder Structure

```text
women-safety-chatbot/
  app.py
  chatbot.py
  emergency.py
  voice_support.py
  location_services.py
  database.py
  self_defense.py
  requirements.txt
  README.md
  assets/
```

## How the App Works

- `app.py` contains the Streamlit UI and integrates every feature.
- `chatbot.py` handles offline response matching and danger keyword detection.
- `database.py` creates and manages the SQLite emergency contacts database.
- `emergency.py` handles SOS messages, emergency instructions, and optional Twilio SMS.
- `location_services.py` simulates GPS location and creates Folium maps.
- `voice_support.py` handles voice input and local text-to-speech.
- `self_defense.py` stores self-defense guidance and quick actions.

## Installation

Open PowerShell in this folder and run:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional spaCy model:

```powershell
python -m spacy download en_core_web_sm
```

The app still runs without the model because it falls back to a blank spaCy pipeline.

## Run Command

```powershell
streamlit run app.py
```

If another Streamlit app is already using port 8501, run:

```powershell
streamlit run app.py --server.port 8502
```

Then open the URL shown in the terminal.

## Optional Twilio Setup

The app works in simulation mode by default. To send real SMS alerts, set these environment variables:

```powershell
$env:TWILIO_ACCOUNT_SID="your_sid"
$env:TWILIO_AUTH_TOKEN="your_token"
$env:TWILIO_FROM_NUMBER="your_twilio_number"
```

Real SMS also requires valid recipient numbers and Twilio account permissions.

## SQLite Database Location

By default, contacts are stored in:

```text
%LOCALAPPDATA%\WomenSafetyChatbot\safety_contacts.db
```

This avoids SQLite disk I/O issues that can happen in OneDrive-synced folders. To use a custom database path:

```powershell
$env:WOMEN_SAFETY_DB_PATH="C:\path\to\safety_contacts.db"
```

## Deployment Guidance

You can deploy this to Streamlit Community Cloud:

1. Push the project to GitHub.
2. Create a new Streamlit app.
3. Select `app.py` as the main file.
4. Keep `requirements.txt` in the project root.
5. Add Twilio secrets only if you want real SMS alerts.

For local college/demo projects, simulation mode is enough and needs no API keys.

## Notes

- Location is simulated for safety and demo purposes.
- Voice input may require microphone access and PyAudio support depending on your system.
- Emergency alerts are simulated unless Twilio credentials are configured.
