# Clash Royale Deck Analyzer

A professional web application that analyzes Clash Royale player profiles and suggests optimal decks based on card levels and current meta strategies.

## Features

- **Player Profile Analysis**: Fetch real player data including trophies, card levels, and current deck
- **Meta Deck Suggestions**: AI-powered recommendations based on 12+ competitive meta decks
- **Card Upgrade Recommendations**: Strategic guidance on which cards to upgrade next
- **Beautiful UI**: Clash Royale-inspired design with premium animations and effects
- **Mobile Responsive**: Optimized for all devices with Bootstrap framework

## Setup Instructions

### 1. Install Dependencies

The required packages are already configured in `pyproject.toml`:

```bash
# Dependencies are automatically installed via packager tool
```

### 2. Configure Clash Royale API Token

**Important**: To fetch real player data, you need a Clash Royale API token.

1. Visit [https://developer.clashroyale.com/](https://developer.clashroyale.com/)
2. Create a developer account with your email
3. Generate an API key for your application
4. Set the environment variable:

```bash
export CLASH_ROYALE_API_TOKEN="your_actual_token_here"
```

Or update the token in `app.py` line 35:
```python
CLASH_ROYALE_API_TOKEN = os.environ.get("CLASH_ROYALE_API_TOKEN", "your_actual_token_here")
```

### 3. Run the Application

```bash
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

The app will be available at `http://localhost:5000`

## API Endpoints

### Player Data
- `GET /api/player/<player_tag>` - Fetch real player profile data
- `GET /api/demo/player/<player_tag>` - Demo mode with sample data

### Deck Analysis
- `GET /api/meta-decks` - Get current meta deck database
- `POST /api/suggest-deck` - Get optimal deck suggestion
- `POST /api/upgrade-suggestion` - Get card upgrade recommendations

## Usage

1. **Enter Player Tag**: Input any Clash Royale player tag (e.g., #2PP)
2. **Get Profile**: Click "Get My Profile" to fetch player data
3. **Suggest Deck**: Click "Suggest Best Deck" for meta-based recommendations
4. **Upgrade Cards**: Click "Card to Upgrade" for strategic upgrade advice

## Demo Mode

If no API token is configured, the app offers a demo mode with sample data to showcase all features.

## Meta Deck Database

The app includes 12 competitive meta decks:
- Log Bait 2.6
- Hog 2.6 Cycle  
- Giant Double Prince
- X-Bow 2.9
- Golem Lightning
- Miner Poison Control
- P.E.K.K.A Bridge Spam
- LavaLoon
- Royal Giant Cycle
- Mortar Bait
- Graveyard Poison
- Mega Knight Ram Rider

## Algorithm Features

### Deck Compatibility Scoring
- **Trophy Range Analysis**: Matches decks to player's competitive level
- **Card Level Assessment**: Evaluates readiness based on current card levels
- **Meta Strength Weighting**: Prioritizes high win-rate decks

### Upgrade Priority Calculation
- **Multi-deck Frequency**: Cards appearing in multiple meta decks get higher priority
- **Level Deficit Analysis**: Identifies cards most in need of upgrades
- **Trophy Range Optimization**: Recommendations tailored to competitive requirements

## Technology Stack

- **Backend**: Python Flask with SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Styling**: Bootstrap 5 + Custom Clash Royale Theme
- **Icons**: Font Awesome 6
- **Fonts**: Google Fonts (Poppins)
- **API**: Official Clash Royale API integration

## File Structure

```
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── models.py           # Database models
├── data/
│   └── meta_decks.json # Meta deck database
├── static/
│   ├── style.css       # Custom styling
│   └── script.js       # Frontend JavaScript
├── templates/
│   └── index.html      # Main application template
└── README.md           # This file
```

## Error Handling

The application includes comprehensive error handling for:
- Invalid player tags
- API rate limiting
- Network connectivity issues
- Missing API token configuration
- Invalid API responses

## Contributing

1. Ensure API token is properly configured
2. Test with both real and demo data
3. Verify responsive design on multiple devices
4. Update meta deck database as needed

## License

This project is for educational and personal use. Clash Royale is a trademark of Supercell.