import os
import logging
import requests
import json
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "clash-royale-deck-app-secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///clash_royale.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Clash Royale API configuration
# TO SETUP: Replace "YOUR_TOKEN_HERE" with your actual API token from https://developer.clashroyale.com/
CLASH_ROYALE_API_TOKEN = os.environ.get("CLASH_ROYALE_API_TOKEN", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImE3NzhhZDlhLWU3NjEtNDc3Ni1hZDRmLWU3ODk0NWUzMGQwYSIsImlhdCI6MTc0OTIyMjIzNiwic3ViIjoiZGV2ZWxvcGVyLzRjMGExNTgwLTM4NjEtZjkwMi0yYTg0LTY3MWIxNjcxMzAxZSIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMDAuMjAuOTIuMTAxIiwiNDQuMjI1LjE4MS43MiIsIjQ0LjIyNy4yMTcuMTQ0IiwiOTQuMTIwLjE5Mi4xMzIiXSwidHlwZSI6ImNsaWVudCJ9XX0.BYe2fb72X85rXFUzREgTXj0moBNLmdYy8Q8aJMVe1PECaARK_xZFzJAbsmneGVpL4DuMFZS_goHetwE0EAwU-Q")
CLASH_ROYALE_API_BASE = "https://api.clashroyale.com/v1"

with app.app_context():
    import models
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/player/<player_tag>')
def get_player_profile(player_tag):
    """Fetch player profile from Clash Royale API"""
    try:
        # Check if API token is properly configured
        if CLASH_ROYALE_API_TOKEN == "YOUR_TOKEN_HERE" or not CLASH_ROYALE_API_TOKEN:
            return jsonify({
                'error': 'API token not configured. Please set up your Clash Royale API token.',
                'errorType': 'configuration',
                'setupInstructions': {
                    'step1': 'Visit https://developer.clashroyale.com/',
                    'step2': 'Create a developer account',
                    'step3': 'Generate an API key',
                    'step4': 'Replace YOUR_TOKEN_HERE in the environment variable'
                }
            }), 500
        
        # Clean player tag
        if not player_tag.startswith('#'):
            player_tag = '#' + player_tag
        
        # URL encode the player tag
        encoded_tag = player_tag.replace('#', '%23')
        
        headers = {
            'Authorization': f'Bearer {CLASH_ROYALE_API_TOKEN}',
            'Accept': 'application/json'
        }
        
        # Get player profile
        player_url = f"{CLASH_ROYALE_API_BASE}/players/{encoded_tag}"
        app.logger.debug(f"Requesting player data from: {player_url}")
        player_response = requests.get(player_url, headers=headers, timeout=15)
        
        app.logger.debug(f"API Response status: {player_response.status_code}")
        
        if player_response.status_code == 200:
            player_data = player_response.json()
            app.logger.debug(f"Player data keys: {list(player_data.keys())}")
            
            # Transform player data for frontend
            transformed_data = {
                'tag': player_data.get('tag', ''),
                'name': player_data.get('name', ''),
                'trophies': player_data.get('trophies', 0),
                'bestTrophies': player_data.get('bestTrophies', 0),
                'expLevel': player_data.get('expLevel', 1),
                'cards': player_data.get('cards', []),
                'currentDeck': player_data.get('currentDeck', []),
                'arena': player_data.get('arena', {}),
                'clan': player_data.get('clan', {})
            }
            
            app.logger.info(f"Successfully fetched profile for {transformed_data['name']} ({transformed_data['tag']})")
            return jsonify(transformed_data)
        else:
            error_msg = f"API Error: {player_response.status_code}"
            if player_response.status_code == 404:
                error_msg = "Player not found. Please check the player tag and try again."
            elif player_response.status_code == 429:
                error_msg = "API rate limit exceeded. Please wait a moment and try again."
            elif player_response.status_code == 403:
                error_msg = "API access denied. Please verify your API token is valid and active."
            elif player_response.status_code == 400:
                error_msg = "Invalid player tag format. Please enter a valid tag (e.g., #2PP)."
            
            app.logger.warning(f"API request failed: {error_msg}")
            return jsonify({'error': error_msg, 'errorType': 'api'}), player_response.status_code
            
    except requests.RequestException as e:
        app.logger.error(f"Request error: {str(e)}")
        return jsonify({
            'error': 'Network connection failed. Please check your internet and try again.',
            'errorType': 'network'
        }), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred. Please try again.',
            'errorType': 'system'
        }), 500

@app.route('/api/demo/player/<player_tag>')
def get_demo_player_profile(player_tag):
    """Demo endpoint with sample data - shows app functionality without requiring API token"""
    # Sample player data for demonstration
    demo_data = {
        'tag': f'#{player_tag.upper()}',
        'name': 'Demo Player',
        'trophies': 6500,
        'bestTrophies': 7200,
        'expLevel': 13,
        'arena': {'name': 'Master III'},
        'clan': {'name': 'Demo Clan'},
        'currentDeck': [
            {'name': 'Hog Rider', 'level': 13},
            {'name': 'Musketeer', 'level': 12},
            {'name': 'Ice Golem', 'level': 11},
            {'name': 'Skeletons', 'level': 12},
            {'name': 'Ice Spirit', 'level': 11},
            {'name': 'Fireball', 'level': 13},
            {'name': 'The Log', 'level': 12},
            {'name': 'Cannon', 'level': 11}
        ],
        'cards': [
            {'name': 'Hog Rider', 'level': 13},
            {'name': 'Musketeer', 'level': 12},
            {'name': 'Ice Golem', 'level': 11},
            {'name': 'Skeletons', 'level': 12},
            {'name': 'Ice Spirit', 'level': 11},
            {'name': 'Fireball', 'level': 13},
            {'name': 'The Log', 'level': 12},
            {'name': 'Cannon', 'level': 11},
            {'name': 'Giant', 'level': 12},
            {'name': 'Prince', 'level': 11},
            {'name': 'Dark Prince', 'level': 10},
            {'name': 'Mega Minion', 'level': 12},
            {'name': 'Electro Wizard', 'level': 11},
            {'name': 'Poison', 'level': 12},
            {'name': 'Zap', 'level': 13},
            {'name': 'Elixir Collector', 'level': 10},
            {'name': 'Knight', 'level': 13},
            {'name': 'Archers', 'level': 12},
            {'name': 'Goblin Barrel', 'level': 11},
            {'name': 'Princess', 'level': 10},
            {'name': 'Rocket', 'level': 11},
            {'name': 'Goblin Gang', 'level': 12},
            {'name': 'Inferno Tower', 'level': 11}
        ]
    }
    
    return jsonify(demo_data)

@app.route('/api/meta-decks')
def get_meta_decks():
    """Get meta decks from JSON file"""
    try:
        with open('data/meta_decks.json', 'r') as f:
            meta_decks = json.load(f)
        return jsonify(meta_decks)
    except Exception as e:
        app.logger.error(f"Error loading meta decks: {str(e)}")
        return jsonify({'error': 'Failed to load meta decks'}), 500

@app.route('/api/suggest-deck', methods=['POST'])
def suggest_deck():
    """Suggest best deck based on player's card levels and trophy range"""
    try:
        data = request.get_json()
        player_cards = data.get('cards', [])
        player_trophies = data.get('trophies', 0)
        
        # Load meta decks
        with open('data/meta_decks.json', 'r') as f:
            meta_data = json.load(f)
            meta_decks = meta_data.get('decks', [])
        
        # Create card level lookup
        card_levels = {}
        for card in player_cards:
            card_levels[card['name']] = card['level']
        
        best_deck = None
        best_score = -1
        
        for deck in meta_decks:
            score = calculate_deck_compatibility(deck, card_levels, player_trophies)
            if score > best_score:
                best_score = score
                best_deck = deck
        
        if best_deck:
            # Add compatibility info
            best_deck['compatibilityScore'] = best_score
            best_deck['playerCardLevels'] = {}
            best_deck['missingLevels'] = {}
            
            for card_name in best_deck['cards']:
                player_level = card_levels.get(card_name, 1)
                recommended_level = best_deck.get('recommendedLevels', {}).get(card_name, 11)
                best_deck['playerCardLevels'][card_name] = player_level
                if player_level < recommended_level:
                    best_deck['missingLevels'][card_name] = recommended_level - player_level
            
            return jsonify(best_deck)
        else:
            return jsonify({'error': 'No suitable deck found'}), 404
            
    except Exception as e:
        app.logger.error(f"Error suggesting deck: {str(e)}")
        return jsonify({'error': 'Failed to suggest deck'}), 500

@app.route('/api/coach-suggestion', methods=['POST'])
def coach_suggestion():
    """Get personalized deck suggestion based on playstyle and card levels"""
    try:
        data = request.get_json()
        player_cards = data.get('cards', [])
        player_trophies = data.get('trophies', 0)
        playstyle = data.get('playstyle', '')
        card_type_preference = data.get('cardType', '')
        disliked_cards = data.get('dislikedCards', '').split(',')
        disliked_cards = [card.strip() for card in disliked_cards if card.strip()]
        
        # Load meta decks
        with open('data/meta_decks.json', 'r') as f:
            meta_data = json.load(f)
            meta_decks = meta_data.get('decks', [])
        
        # Create card level lookup
        card_levels = {}
        for card in player_cards:
            card_levels[card['name']] = card['level']
        
        # Find best deck with playstyle consideration
        best_deck = find_personalized_deck(meta_decks, card_levels, player_trophies, 
                                         playstyle, card_type_preference, disliked_cards)
        
        if best_deck:
            # Generate coaching explanation
            coaching_analysis = generate_coaching_analysis(best_deck, playstyle, 
                                                         card_type_preference, card_levels, player_trophies)
            
            best_deck['coachingAnalysis'] = coaching_analysis
            return jsonify(best_deck)
        else:
            return jsonify({'error': 'No suitable deck found for your preferences'}), 404
            
    except Exception as e:
        app.logger.error(f"Error generating coach suggestion: {str(e)}")
        return jsonify({'error': 'Failed to generate coaching suggestion'}), 500

@app.route('/api/playing-tips', methods=['POST'])
def get_playing_tips():
    """Get personalized playing tips for the recommended deck"""
    try:
        data = request.get_json()
        deck_name = data.get('deckName', '')
        player_trophies = data.get('trophies', 0)
        playstyle = data.get('playstyle', '')
        
        tips = generate_playing_tips(deck_name, player_trophies, playstyle)
        
        return jsonify({
            'tips': tips,
            'trophyRange': get_trophy_range_info(player_trophies)
        })
        
    except Exception as e:
        app.logger.error(f"Error generating playing tips: {str(e)}")
        return jsonify({'error': 'Failed to generate playing tips'}), 500

@app.route('/api/upgrade-suggestion', methods=['POST'])
def upgrade_suggestion():
    """Suggest which card to upgrade next"""
    try:
        data = request.get_json()
        player_cards = data.get('cards', [])
        player_trophies = data.get('trophies', 0)
        playstyle = data.get('playstyle', '')
        
        # Load meta decks
        with open('data/meta_decks.json', 'r') as f:
            meta_data = json.load(f)
            meta_decks = meta_data.get('decks', [])
        
        # Create card level lookup
        card_levels = {}
        for card in player_cards:
            card_levels[card['name']] = card['level']
        
        # Calculate upgrade priorities with playstyle consideration
        upgrade_priorities = calculate_upgrade_priorities_with_playstyle(
            meta_decks, card_levels, player_trophies, playstyle)
        
        if upgrade_priorities:
            return jsonify({
                'recommendations': upgrade_priorities[:5],  # Top 5 recommendations
                'trophyRange': get_trophy_range_info(player_trophies),
                'coachAdvice': generate_upgrade_coaching_advice(upgrade_priorities[:3], player_trophies)
            })
        else:
            return jsonify({'error': 'No upgrade recommendations available'}), 404
            
    except Exception as e:
        app.logger.error(f"Error calculating upgrade suggestion: {str(e)}")
        return jsonify({'error': 'Failed to calculate upgrade suggestion'}), 500

def calculate_deck_compatibility(deck, card_levels, player_trophies):
    """Calculate compatibility score for a deck based on card levels and trophy range"""
    total_score = 0
    deck_cards = deck.get('cards', [])
    recommended_levels = deck.get('recommendedLevels', {})
    min_trophy_range = deck.get('minTrophies', 0)
    optimal_trophy_range = deck.get('optimalTrophies', 5000)
    
    if len(deck_cards) == 0:
        return 0
    
    # Trophy range compatibility (30% of score)
    trophy_score = 0
    if player_trophies >= optimal_trophy_range:
        trophy_score = 30
    elif player_trophies >= min_trophy_range:
        trophy_ratio = (player_trophies - min_trophy_range) / (optimal_trophy_range - min_trophy_range)
        trophy_score = 15 + (trophy_ratio * 15)
    else:
        # Penalty for being below minimum trophy range
        trophy_score = max(0, 15 - ((min_trophy_range - player_trophies) / 500))
    
    total_score += trophy_score
    
    # Card level compatibility (70% of score)
    card_score = 0
    for card_name in deck_cards:
        player_level = card_levels.get(card_name, 1)
        recommended_level = recommended_levels.get(card_name, 11)
        
        if player_level >= recommended_level:
            # Perfect level match
            card_score += 10
        elif player_level >= recommended_level - 1:
            # One level below recommended
            card_score += 8
        elif player_level >= recommended_level - 2:
            # Two levels below recommended
            card_score += 5
        elif player_level >= recommended_level - 3:
            # Three levels below recommended
            card_score += 2
        else:
            # Too far below recommended level
            card_score += 0
    
    # Average card score
    average_card_score = card_score / len(deck_cards)
    total_score += average_card_score * 7  # Scale to 70% of total
    
    # Meta strength bonus (deck win rate consideration)
    meta_strength = deck.get('winRate', 50)
    if meta_strength > 55:
        total_score += 5
    elif meta_strength > 52:
        total_score += 2
    
    return total_score

def calculate_upgrade_priorities(meta_decks, card_levels, player_trophies):
    """Calculate which cards should be upgraded first"""
    card_priorities = {}
    
    # Find cards that appear in multiple meta decks suitable for player's trophy range
    for deck in meta_decks:
        min_trophies = deck.get('minTrophies', 0)
        if player_trophies >= min_trophies - 500:  # Include decks slightly above player level
            deck_weight = deck.get('winRate', 50) / 50  # Weight by win rate
            recommended_levels = deck.get('recommendedLevels', {})
            
            for card_name in deck.get('cards', []):
                player_level = card_levels.get(card_name, 1)
                recommended_level = recommended_levels.get(card_name, 11)
                
                if card_name not in card_priorities:
                    card_priorities[card_name] = {
                        'card': card_name,
                        'currentLevel': player_level,
                        'recommendedLevel': recommended_level,
                        'priority': 0,
                        'appearsInDecks': 0,
                        'averageWinRate': 0,
                        'levelDeficit': max(0, recommended_level - player_level)
                    }
                
                card_priorities[card_name]['appearsInDecks'] += 1
                card_priorities[card_name]['averageWinRate'] += deck.get('winRate', 50)
                
                # Higher priority for cards that are under-leveled in high-win-rate decks
                if player_level < recommended_level:
                    priority_boost = (recommended_level - player_level) * deck_weight
                    card_priorities[card_name]['priority'] += priority_boost
    
    # Calculate final priorities
    for card_name, info in card_priorities.items():
        if info['appearsInDecks'] > 0:
            info['averageWinRate'] = info['averageWinRate'] / info['appearsInDecks']
            # Boost priority for cards that appear in multiple decks
            info['priority'] += info['appearsInDecks'] * 2
            # Boost for cards with level deficit
            info['priority'] += info['levelDeficit'] * 3
    
    # Sort by priority and filter only cards that need upgrades
    sorted_priorities = sorted(
        [info for info in card_priorities.values() if info['levelDeficit'] > 0],
        key=lambda x: x['priority'],
        reverse=True
    )
    
    return sorted_priorities

def find_personalized_deck(meta_decks, card_levels, player_trophies, playstyle, card_type_preference, disliked_cards):
    """Find the best deck based on playstyle preferences and card levels"""
    best_deck = None
    best_score = -1
    
    for deck in meta_decks:
        # Skip decks with disliked cards
        if any(disliked_card in deck.get('cards', []) for disliked_card in disliked_cards):
            continue
        
        # Calculate base compatibility
        base_score = calculate_deck_compatibility(deck, card_levels, player_trophies)
        
        # Add playstyle bonus
        playstyle_bonus = calculate_playstyle_match(deck, playstyle, card_type_preference)
        
        # Calculate card level advantage (prefer higher level cards)
        level_bonus = calculate_level_advantage(deck, card_levels)
        
        total_score = base_score + playstyle_bonus + level_bonus
        
        if total_score > best_score:
            best_score = total_score
            best_deck = deck.copy()
    
    if best_deck:
        # Add personalization metadata
        best_deck['compatibilityScore'] = best_score
        best_deck['styleMatch'] = calculate_playstyle_match(best_deck, playstyle, card_type_preference)
        best_deck['playerCardLevels'] = {}
        best_deck['missingLevels'] = {}
        
        for card_name in best_deck['cards']:
            player_level = card_levels.get(card_name, 1)
            recommended_level = best_deck.get('recommendedLevels', {}).get(card_name, 11)
            best_deck['playerCardLevels'][card_name] = player_level
            if player_level < recommended_level:
                best_deck['missingLevels'][card_name] = recommended_level - player_level
    
    return best_deck

def calculate_playstyle_match(deck, playstyle, card_type_preference):
    """Calculate how well a deck matches the player's playstyle preferences"""
    score = 0
    deck_archetype = deck.get('archetype', '').lower()
    
    # Playstyle matching
    if playstyle == 'control' and deck_archetype in ['control']:
        score += 25
    elif playstyle == 'beatdown' and deck_archetype in ['beatdown']:
        score += 25
    elif playstyle == 'cycle' and deck_archetype in ['cycle']:
        score += 25
    elif playstyle == 'siege' and deck_archetype in ['siege']:
        score += 25
    elif playstyle == 'control' and deck_archetype in ['bridge spam']:
        score += 15  # Partial match
    elif playstyle == 'beatdown' and deck_archetype in ['bridge spam']:
        score += 10  # Some overlap
    
    # Card type preference bonus
    cards = deck.get('cards', [])
    spell_cards = ['Fireball', 'Lightning', 'Rocket', 'Poison', 'Arrows', 'The Log', 'Zap', 'Freeze', 'Tornado']
    win_condition_cards = ['Hog Rider', 'Giant', 'Golem', 'X-Bow', 'Mortar', 'Graveyard', 'Miner', 'Royal Giant']
    building_cards = ['Cannon', 'Tesla', 'Inferno Tower', 'Tombstone', 'Elixir Collector']
    
    if card_type_preference == 'spells':
        spell_count = len([card for card in cards if card in spell_cards])
        score += spell_count * 5
    elif card_type_preference == 'winConditions':
        win_condition_count = len([card for card in cards if card in win_condition_cards])
        score += win_condition_count * 8
    elif card_type_preference == 'buildings':
        building_count = len([card for card in cards if card in building_cards])
        score += building_count * 10
    elif card_type_preference == 'support':
        support_count = len([card for card in cards if card not in spell_cards + win_condition_cards + building_cards])
        score += min(support_count, 4) * 3
    
    return min(score, 100)  # Cap at 100

def calculate_level_advantage(deck, card_levels):
    """Calculate bonus for using player's higher-level cards"""
    total_bonus = 0
    cards = deck.get('cards', [])
    
    for card_name in cards:
        player_level = card_levels.get(card_name, 1)
        # Bonus for higher level cards (encourages using maxed cards)
        if player_level >= 13:
            total_bonus += 15
        elif player_level >= 11:
            total_bonus += 10
        elif player_level >= 9:
            total_bonus += 5
    
    return min(total_bonus, 50)  # Cap the bonus

def generate_coaching_analysis(deck, playstyle, card_type_preference, card_levels, player_trophies):
    """Generate personalized coaching analysis"""
    analysis = f"Based on your preference for {playstyle} decks"
    
    if card_type_preference:
        analysis += f" and {card_type_preference}"
    
    analysis += f", I've selected this {deck.get('archetype', 'meta')} deck for you. "
    
    # Analyze card levels
    high_level_cards = [card for card in deck['cards'] if card_levels.get(card, 1) >= 12]
    if high_level_cards:
        analysis += f"This deck takes advantage of your high-level cards: {', '.join(high_level_cards[:3])}. "
    
    # Trophy range advice
    trophy_info = get_trophy_range_info(player_trophies)
    if trophy_info['competitive']:
        analysis += f"At {player_trophies} trophies in {trophy_info['range']}, this deck's {deck.get('winRate', 50)}% win rate makes it competitive for ladder climbing."
    else:
        analysis += f"This deck will help you progress from {trophy_info['range']} to higher arenas."
    
    return analysis

def generate_playing_tips(deck_name, player_trophies, playstyle):
    """Generate personalized playing tips for the deck"""
    tips = []
    
    # Deck-specific tips
    deck_tips = {
        'Hog 2.6 Cycle': [
            'Keep your elixir count low to outcycle your opponent',
            'Use Ice Golem to kite tanks and protect your Hog Rider',
            'Save your Cannon for defense and use Musketeer for both offense and defense',
            'Master the timing of your Hog Rider pushes after your opponent commits elixir'
        ],
        'Log Bait 2.6': [
            'Always have a spell bait card ready before using Goblin Barrel',
            'Use Princess to apply pressure and bait out The Log',
            'Defend with cheap troops and counter-push with Goblin Barrel',
            'Save Rocket for clutch tower damage or eliminating key defensive units'
        ],
        'Giant Double Prince': [
            'Build up elixir advantage with Elixir Collector when possible',
            'Use Giant as a tank for your Prince cards',
            'Apply pressure in both lanes to overwhelm your opponent',
            'Save Poison for swarm troops and support units behind tanks'
        ]
    }
    
    if deck_name in deck_tips:
        tips.extend(deck_tips[deck_name])
    
    # Playstyle-specific tips
    if playstyle == 'control':
        tips.append('Focus on positive elixir trades and defend until you can make a strong counter-push')
        tips.append('Use your defensive buildings to pull tanks and buy time for your troops')
    elif playstyle == 'beatdown':
        tips.append('Build up big pushes behind your tank unit during double elixir time')
        tips.append('Don\'t be afraid to take some tower damage while building your counter-push')
    elif playstyle == 'cycle':
        tips.append('Keep your hand cycling and maintain constant pressure')
        tips.append('Learn to defend with minimal elixir to maintain your cycle advantage')
    elif playstyle == 'siege':
        tips.append('Protect your siege building at all costs with defensive troops')
        tips.append('Apply pressure when your opponent is low on elixir or out of position')
    
    # Trophy-specific tips
    trophy_info = get_trophy_range_info(player_trophies)
    if trophy_info['competitive']:
        tips.append('Focus on perfecting your micro-management and card timings')
        tips.append('Study common matchups and prepare specific strategies for each')
    else:
        tips.append('Focus on learning basic game mechanics and card interactions')
        tips.append('Practice proper elixir management and avoid overcommitting')
    
    return tips[:6]  # Return top 6 tips

def calculate_upgrade_priorities_with_playstyle(meta_decks, card_levels, player_trophies, playstyle):
    """Calculate upgrade priorities considering playstyle preferences"""
    card_priorities = {}
    
    for deck in meta_decks:
        # Give higher weight to decks matching playstyle
        deck_archetype = deck.get('archetype', '').lower()
        playstyle_weight = 1.0
        
        if playstyle == 'control' and deck_archetype in ['control']:
            playstyle_weight = 2.0
        elif playstyle == 'beatdown' and deck_archetype in ['beatdown']:
            playstyle_weight = 2.0
        elif playstyle == 'cycle' and deck_archetype in ['cycle']:
            playstyle_weight = 2.0
        elif playstyle == 'siege' and deck_archetype in ['siege']:
            playstyle_weight = 2.0
        
        min_trophies = deck.get('minTrophies', 0)
        if player_trophies >= min_trophies - 500:
            deck_weight = (deck.get('winRate', 50) / 50) * playstyle_weight
            recommended_levels = deck.get('recommendedLevels', {})
            
            for card_name in deck.get('cards', []):
                player_level = card_levels.get(card_name, 1)
                recommended_level = recommended_levels.get(card_name, 11)
                
                if card_name not in card_priorities:
                    card_priorities[card_name] = {
                        'card': card_name,
                        'currentLevel': player_level,
                        'recommendedLevel': recommended_level,
                        'priority': 0,
                        'appearsInDecks': 0,
                        'averageWinRate': 0,
                        'levelDeficit': max(0, recommended_level - player_level)
                    }
                
                card_priorities[card_name]['appearsInDecks'] += 1
                card_priorities[card_name]['averageWinRate'] += deck.get('winRate', 50)
                
                if player_level < recommended_level:
                    priority_boost = (recommended_level - player_level) * deck_weight
                    card_priorities[card_name]['priority'] += priority_boost
    
    # Calculate final priorities
    for card_name, info in card_priorities.items():
        if info['appearsInDecks'] > 0:
            info['averageWinRate'] = info['averageWinRate'] / info['appearsInDecks']
            info['priority'] += info['appearsInDecks'] * 2
            info['priority'] += info['levelDeficit'] * 3
    
    sorted_priorities = sorted(
        [info for info in card_priorities.values() if info['levelDeficit'] > 0],
        key=lambda x: x['priority'],
        reverse=True
    )
    
    return sorted_priorities

def generate_upgrade_coaching_advice(top_upgrades, player_trophies):
    """Generate coaching advice for upgrades"""
    if not top_upgrades:
        return "Your cards are well-leveled for your current trophy range!"
    
    advice = f"Focus on upgrading {top_upgrades[0]['card']} first - it appears in multiple meta decks "
    advice += f"and needs {top_upgrades[0]['levelDeficit']} level(s) to be competitive. "
    
    if len(top_upgrades) > 1:
        advice += f"Then prioritize {top_upgrades[1]['card']} for better ladder performance."
    
    trophy_info = get_trophy_range_info(player_trophies)
    if trophy_info['competitive']:
        advice += " At your trophy level, even small level advantages can make a significant difference."
    
    return advice

def get_trophy_range_info(trophies):
    """Get information about trophy range and recommended card levels"""
    if trophies >= 7000:
        return {
            'range': 'Champion League',
            'recommendedCardLevel': '14-15',
            'competitive': True
        }
    elif trophies >= 6000:
        return {
            'range': 'Master League',
            'recommendedCardLevel': '13-14',
            'competitive': True
        }
    elif trophies >= 5000:
        return {
            'range': 'Challenger League',
            'recommendedCardLevel': '11-13',
            'competitive': True
        }
    elif trophies >= 4000:
        return {
            'range': 'Spooky Town+',
            'recommendedCardLevel': '10-12',
            'competitive': False
        }
    else:
        return {
            'range': 'Lower Arenas',
            'recommendedCardLevel': '8-11',
            'competitive': False
        }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
