# CB Auto DJ

CB Auto DJ is a Python application that monitors a JSON long polling REST API for incoming events. It identifies token tipping events with specific criteria and processes messages to queue songs on Spotify using OpenAI's GPT-4 API to extract song titles.

## Features

- Monitor a REST API for token tipping events.
- Validate tip amounts and process specific messages.
- Use OpenAI GPT-4 API to extract song titles from messages.
- Queue identified songs on Spotify for playback.

## Requirements

- Python 3.7+
- An OpenAI API key
- Spotify Developer credentials (Client ID, Client Secret, Redirect URI)

## Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/yourusername/cb-auto-dj.git
    cd cb-auto-dj
    ```

2. **Create and activate a virtual environment**:

    ```sh
    python -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

4. **Set up configuration**:
    - Copy `config.ini.example` to `config.ini` and fill in your OpenAI and Spotify credentials.

5. **Run the application**:

    ```sh
    python cbautodj/autodj.py
    ```

## Configuration

Edit the `config.ini` file to include your API keys and other settings:

```ini
[OPENAI]
api_key = your_openai_api_key

[SPOTIFY]
client_id = your_spotify_client_id
client_secret = your_spotify_client_secret
redirect_uri = http://localhost:8888/callback
```

## Usage

1. **Monitoring API**:
    The application continuously monitors the specified API URL for events.

2. **Handling Events**:
    When a token tipping event is detected, it checks the tip amount and processes the message if the criteria are met.

3. **Queueing Songs**:
    The extracted song titles from the message are searched on Spotify and added to the playback queue.

## Development

- Ensure all changes are well-documented.
- Implement unit tests for new features.
- Follow PEP 8 guidelines for code style.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## Contact

For any questions or feedback, please open an issue or contact the project maintainers.
