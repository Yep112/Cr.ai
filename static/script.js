// Global variables to store player data and preferences
let playerData = null;
let metaDecks = null;
let playerPreferences = {
    playstyle: '',
    cardType: '',
    dislikedCards: ''
};

// DOM elements
const playerTagInput = document.getElementById('playerTagInput');
const getProfileBtn = document.getElementById('getProfileBtn');
const suggestDeckBtn = document.getElementById('suggestDeckBtn');
const upgradeCardBtn = document.getElementById('upgradeCardBtn');
const playingTipsBtn = document.getElementById('playingTipsBtn');
const getCoachingBtn = document.getElementById('getCoachingBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorAlert = document.getElementById('errorAlert');
const errorMessage = document.getElementById('errorMessage');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    getProfileBtn.addEventListener('click', getPlayerProfile);
    suggestDeckBtn.addEventListener('click', getPersonalizedDeckCoaching);
    upgradeCardBtn.addEventListener('click', getUpgradeSuggestion);
    playingTipsBtn.addEventListener('click', getPlayingTips);
    getCoachingBtn.addEventListener('click', getPersonalizedDeckCoaching);
    
    // Allow enter key in input field
    playerTagInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            getPlayerProfile();
        }
    });
    
    // Load meta decks on page load
    loadMetaDecks();
});

// Utility functions
function showLoading() {
    loadingIndicator.style.display = 'block';
    hideError();
}

function hideLoading() {
    loadingIndicator.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorAlert.style.display = 'block';
    hideLoading();
}

function hideError() {
    errorAlert.style.display = 'none';
}

function validatePlayerTag(tag) {
    // Remove # if present and validate format
    const cleanTag = tag.replace('#', '').toUpperCase();
    if (cleanTag.length < 3 || cleanTag.length > 10) {
        return false;
    }
    // Check if contains only valid characters (letters and numbers, some special chars)
    return /^[0-9A-Z]+$/.test(cleanTag);
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function getTrophyRangeInfo(trophies) {
    if (trophies >= 7000) {
        return { range: 'Champion League', level: '14-15', competitive: true, color: 'danger' };
    } else if (trophies >= 6000) {
        return { range: 'Master League', level: '13-14', competitive: true, color: 'warning' };
    } else if (trophies >= 5000) {
        return { range: 'Challenger League', level: '11-13', competitive: true, color: 'info' };
    } else if (trophies >= 4000) {
        return { range: 'Spooky Town+', level: '10-12', competitive: false, color: 'success' };
    } else {
        return { range: 'Lower Arenas', level: '8-11', competitive: false, color: 'secondary' };
    }
}

function getCardIcon(cardName) {
    // Map card names to Font Awesome icons
    const iconMap = {
        'Knight': 'fas fa-shield-alt',
        'Archers': 'fas fa-bow-arrow',
        'Goblins': 'fas fa-users',
        'Giant': 'fas fa-fist-raised',
        'Wizard': 'fas fa-magic',
        'Dragon': 'fas fa-dragon',
        'P.E.K.K.A': 'fas fa-robot',
        'Minions': 'fas fa-crow',
        'Balloon': 'fas fa-parachute-box',
        'Witch': 'fas fa-hat-wizard',
        'Barbarians': 'fas fa-axe-battle',
        'Hog Rider': 'fas fa-horse',
        'Valkyrie': 'fas fa-axe',
        'Skeleton Army': 'fas fa-skull',
        'Freeze': 'fas fa-snowflake',
        'Arrows': 'fas fa-location-arrow',
        'Fireball': 'fas fa-fire-alt',
        'Zap': 'fas fa-bolt',
        'Mirror': 'fas fa-mirror',
        'Tombstone': 'fas fa-monument',
        'Giant Skeleton': 'fas fa-skull-crossbones',
        'Wall Breakers': 'fas fa-bomb',
        'Lightning': 'fas fa-bolt',
        'Rocket': 'fas fa-rocket',
        'Goblin Barrel': 'fas fa-wine-bottle',
        'Tornado': 'fas fa-wind',
        'Clone': 'fas fa-clone',
        'Earthquake': 'fas fa-mountain',
        'Heal Spirit': 'fas fa-heart',
        'Ice Spirit': 'fas fa-snowflake',
        'Fire Spirit': 'fas fa-fire',
        'Electro Spirit': 'fas fa-bolt'
    };
    
    return iconMap[cardName] || 'fas fa-square';
}

function getCardLevelClass(currentLevel, recommendedLevel) {
    if (currentLevel >= recommendedLevel) {
        return 'level-good';
    } else if (currentLevel >= recommendedLevel - 1) {
        return 'level-warning';
    } else {
        return 'level-danger';
    }
}

// Load meta decks data
async function loadMetaDecks() {
    try {
        const response = await fetch('/api/meta-decks');
        if (response.ok) {
            const data = await response.json();
            metaDecks = data.decks;
        } else {
            console.error('Failed to load meta decks');
        }
    } catch (error) {
        console.error('Error loading meta decks:', error);
    }
}

// Get player profile from API
async function getPlayerProfile() {
    const playerTag = playerTagInput.value.trim();
    
    if (!playerTag) {
        showError('Please enter a player tag');
        return;
    }
    
    if (!validatePlayerTag(playerTag)) {
        showError('Invalid player tag format. Please enter a valid Clash Royale player tag (e.g., #2PP)');
        return;
    }
    
    showLoading();
    
    try {
        const cleanTag = playerTag.replace('#', '');
        const response = await fetch(`/api/player/${cleanTag}`);
        
        if (response.ok) {
            playerData = await response.json();
            displayPlayerProfile(playerData);
            hideLoading();
        } else {
            const errorData = await response.json();
            
            // Handle API token configuration error specifically
            if (errorData.errorType === 'configuration') {
                showApiSetupError(errorData);
            } else {
                showError(errorData.error || 'Failed to fetch player profile');
            }
        }
    } catch (error) {
        showError('Network error. Please check your connection and try again.');
        console.error('Error fetching player profile:', error);
    }
}

// Show API setup instructions
function showApiSetupError(errorData) {
    const setupHtml = `
        <div class="alert alert-info mb-3">
            <h5><i class="fas fa-info-circle me-2"></i>API Token Setup Required</h5>
            <p class="mb-3">To fetch real player data, you need to configure a Clash Royale API token:</p>
            <ol class="mb-3">
                <li>Visit <a href="https://developer.clashroyale.com/" target="_blank" class="text-decoration-none">https://developer.clashroyale.com/</a></li>
                <li>Create a developer account</li>
                <li>Generate an API key for your application</li>
                <li>Add the token to your environment variables</li>
            </ol>
            <button id="tryDemoBtn" class="btn btn-success">
                <i class="fas fa-play me-2"></i>Try Demo Mode Instead
            </button>
        </div>
    `;
    
    errorMessage.innerHTML = setupHtml;
    errorAlert.style.display = 'block';
    hideLoading();
    
    // Add demo mode button handler
    document.getElementById('tryDemoBtn').addEventListener('click', function() {
        const playerTag = playerTagInput.value.trim() || 'DEMO';
        tryDemoMode(playerTag);
    });
}

// Try demo mode with sample data
async function tryDemoMode(playerTag) {
    showLoading();
    hideError();
    
    try {
        const cleanTag = playerTag.replace('#', '');
        const response = await fetch(`/api/demo/player/${cleanTag}`);
        
        if (response.ok) {
            playerData = await response.json();
            displayPlayerProfile(playerData);
            hideLoading();
            
            // Show demo mode indicator
            const demoIndicator = document.createElement('div');
            demoIndicator.className = 'alert alert-warning mt-3';
            demoIndicator.innerHTML = `
                <i class="fas fa-flask me-2"></i>
                <strong>Demo Mode:</strong> This is sample data. Configure your API token to fetch real player profiles.
            `;
            document.getElementById('playerProfile').appendChild(demoIndicator);
        } else {
            showError('Demo mode failed to load');
        }
    } catch (error) {
        showError('Demo mode error. Please try again.');
        console.error('Error in demo mode:', error);
    }
}

// Display player profile
function displayPlayerProfile(data) {
    document.getElementById('playerName').textContent = data.name;
    document.getElementById('playerTag').textContent = data.tag;
    document.getElementById('currentTrophies').textContent = formatNumber(data.trophies);
    document.getElementById('bestTrophies').textContent = formatNumber(data.bestTrophies);
    document.getElementById('expLevel').textContent = data.expLevel;
    document.getElementById('totalCards').textContent = data.cards.length;
    
    // Show trophy range warning if needed
    const trophyInfo = getTrophyRangeInfo(data.trophies);
    if (trophyInfo.competitive) {
        const warningElement = document.getElementById('trophyWarning');
        const warningText = document.getElementById('trophyWarningText');
        warningText.textContent = `You're in ${trophyInfo.range}! Recommended card levels: ${trophyInfo.level} for competitive play.`;
        warningElement.style.display = 'block';
    }
    
    // Display current deck if available
    if (data.currentDeck && data.currentDeck.length > 0) {
        displayCurrentDeck(data.currentDeck);
    }
    
    // Show profile and playstyle assessment
    document.getElementById('playerProfile').style.display = 'block';
    document.getElementById('playstyleAssessment').style.display = 'block';
    
    // Add animations
    document.getElementById('playerProfile').classList.add('fade-in');
    document.getElementById('playstyleAssessment').classList.add('slide-up');
}

// Display current deck
function displayCurrentDeck(currentDeck) {
    const currentDeckElement = document.getElementById('currentDeck');
    const currentDeckCards = document.getElementById('currentDeckCards');
    
    currentDeckCards.innerHTML = '';
    
    currentDeck.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'deck-card-item';
        cardElement.innerHTML = `
            <div class="card-icon">
                <i class="${getCardIcon(card.name)}"></i>
            </div>
            <div class="card-name">${card.name}</div>
            <div class="card-level level-good">Lv ${card.level}</div>
        `;
        currentDeckCards.appendChild(cardElement);
    });
    
    currentDeckElement.style.display = 'block';
    currentDeckElement.classList.add('fade-in');
}

// Get personalized deck coaching
async function getPersonalizedDeckCoaching() {
    if (!playerData) {
        showError('Please get your profile first');
        return;
    }
    
    // Collect playstyle preferences
    const playstyleInputs = document.querySelectorAll('input[name="playstyle"]:checked');
    const cardTypeInputs = document.querySelectorAll('input[name="cardType"]:checked');
    const dislikedCardsInput = document.getElementById('dislikedCards');
    
    if (playstyleInputs.length === 0) {
        showError('Please select your preferred playstyle');
        return;
    }
    
    if (cardTypeInputs.length === 0) {
        showError('Please select your preferred card type');
        return;
    }
    
    playerPreferences.playstyle = playstyleInputs[0].value;
    playerPreferences.cardType = cardTypeInputs[0].value;
    playerPreferences.dislikedCards = dislikedCardsInput.value;
    
    showLoading();
    
    try {
        const response = await fetch('/api/coach-suggestion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cards: playerData.cards,
                trophies: playerData.trophies,
                playstyle: playerPreferences.playstyle,
                cardType: playerPreferences.cardType,
                dislikedCards: playerPreferences.dislikedCards
            })
        });
        
        if (response.ok) {
            const coaching = await response.json();
            displayPersonalizedDeckCoaching(coaching);
            hideLoading();
            
            // Show action buttons after coaching
            document.getElementById('actionButtons').style.display = 'block';
            document.getElementById('actionButtons').classList.add('fade-in');
        } else {
            const errorData = await response.json();
            showError(errorData.error || 'Failed to get personalized coaching');
        }
    } catch (error) {
        showError('Error getting personalized coaching. Please try again.');
        console.error('Error getting coaching:', error);
    }
}

// Display personalized deck coaching
function displayPersonalizedDeckCoaching(coaching) {
    // Hide playstyle assessment
    document.getElementById('playstyleAssessment').style.display = 'none';
    
    // Update coaching analysis
    document.getElementById('coachRecommendation').textContent = coaching.coachingAnalysis;
    
    // Update deck info
    document.getElementById('deckName').textContent = coaching.name;
    document.getElementById('deckDescription').textContent = coaching.description;
    document.getElementById('deckWinRate').textContent = coaching.winRate.toFixed(1);
    document.getElementById('deckCompatibility').textContent = Math.round(coaching.compatibilityScore);
    document.getElementById('styleMatch').textContent = Math.round(coaching.styleMatch);
    
    const deckCardsElement = document.getElementById('deckCards');
    deckCardsElement.innerHTML = '';
    
    const warnings = [];
    const explanations = [];
    
    coaching.cards.forEach(cardName => {
        const playerLevel = coaching.playerCardLevels[cardName] || 1;
        const recommendedLevel = coaching.recommendedLevels[cardName] || 11;
        const levelDifference = coaching.missingLevels[cardName] || 0;
        
        const cardElement = document.createElement('div');
        let cardClass = 'deck-card-item';
        
        if (levelDifference > 0) {
            cardClass += ' under-leveled';
            warnings.push(`${cardName}: Need ${levelDifference} more level${levelDifference > 1 ? 's' : ''}`);
        } else {
            cardClass += ' well-leveled';
            if (playerLevel >= 13) {
                explanations.push(`${cardName} is maxed - excellent!`);
            }
        }
        
        cardElement.className = cardClass;
        cardElement.innerHTML = `
            <div class="card-icon">
                <i class="${getCardIcon(cardName)}"></i>
            </div>
            <div class="card-name">${cardName}</div>
            <div class="card-level ${getCardLevelClass(playerLevel, recommendedLevel)}">
                Lv ${playerLevel}/${recommendedLevel}
            </div>
        `;
        deckCardsElement.appendChild(cardElement);
    });
    
    // Display warnings and explanations
    const warningsElement = document.getElementById('deckWarnings');
    if (warnings.length > 0) {
        warningsElement.innerHTML = `
            <div class="alert alert-warning">
                <strong><i class="fas fa-exclamation-triangle me-2"></i>Card Level Recommendations:</strong>
                <ul class="mb-0 mt-2">
                    ${warnings.map(warning => `<li>${warning}</li>`).join('')}
                </ul>
            </div>
        `;
    } else {
        warningsElement.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                <strong>Perfect!</strong> Your card levels are optimal for this deck.
            </div>
        `;
    }
    
    // Generate deck explanation
    let explanation = `This ${coaching.archetype} deck perfectly matches your ${playerPreferences.playstyle} playstyle preference. `;
    explanation += `With a ${coaching.winRate}% win rate in the current meta, it's proven effective for climbing. `;
    
    if (explanations.length > 0) {
        explanation += `Your high-level cards (${explanations.slice(0, 2).map(e => e.split(' is')[0]).join(', ')}) give you a strong foundation. `;
    }
    
    explanation += `The average elixir cost of ${coaching.averageElixir} makes it ${coaching.averageElixir < 3.5 ? 'fast-paced and aggressive' : 'strategic with powerful pushes'}.`;
    
    document.getElementById('deckExplanation').textContent = explanation;
    
    document.getElementById('deckSuggestion').style.display = 'block';
    document.getElementById('deckSuggestion').classList.add('fade-in');
}

// Display deck suggestion
function displayDeckSuggestion(deck) {
    document.getElementById('deckName').textContent = deck.name;
    document.getElementById('deckDescription').textContent = deck.description;
    document.getElementById('deckWinRate').textContent = deck.winRate.toFixed(1);
    document.getElementById('deckCompatibility').textContent = Math.round(deck.compatibilityScore);
    
    const deckCardsElement = document.getElementById('deckCards');
    deckCardsElement.innerHTML = '';
    
    const warnings = [];
    
    deck.cards.forEach(cardName => {
        const playerLevel = deck.playerCardLevels[cardName] || 1;
        const recommendedLevel = deck.recommendedLevels[cardName] || 11;
        const levelDifference = deck.missingLevels[cardName] || 0;
        
        const cardElement = document.createElement('div');
        let cardClass = 'deck-card-item';
        
        if (levelDifference > 0) {
            cardClass += ' under-leveled';
            warnings.push(`${cardName}: Need ${levelDifference} more level${levelDifference > 1 ? 's' : ''}`);
        } else {
            cardClass += ' well-leveled';
        }
        
        cardElement.className = cardClass;
        cardElement.innerHTML = `
            <div class="card-icon">
                <i class="${getCardIcon(cardName)}"></i>
            </div>
            <div class="card-name">${cardName}</div>
            <div class="card-level ${getCardLevelClass(playerLevel, recommendedLevel)}">
                Lv ${playerLevel}/${recommendedLevel}
            </div>
        `;
        deckCardsElement.appendChild(cardElement);
    });
    
    // Display warnings
    const warningsElement = document.getElementById('deckWarnings');
    if (warnings.length > 0) {
        warningsElement.innerHTML = `
            <div class="alert alert-warning">
                <strong><i class="fas fa-exclamation-triangle me-2"></i>Card Level Warnings:</strong>
                <ul class="mb-0 mt-2">
                    ${warnings.map(warning => `<li>${warning}</li>`).join('')}
                </ul>
            </div>
        `;
    } else {
        warningsElement.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                <strong>Perfect!</strong> Your card levels are optimal for this deck.
            </div>
        `;
    }
    
    document.getElementById('deckSuggestion').style.display = 'block';
    document.getElementById('deckSuggestion').classList.add('fade-in');
}

// Get upgrade suggestion
async function getUpgradeSuggestion() {
    if (!playerData) {
        showError('Please get your profile first');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/upgrade-suggestion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cards: playerData.cards,
                trophies: playerData.trophies,
                playstyle: playerPreferences.playstyle
            })
        });
        
        if (response.ok) {
            const upgradeData = await response.json();
            displayUpgradeSuggestion(upgradeData);
            hideLoading();
        } else {
            const errorData = await response.json();
            showError(errorData.error || 'Failed to get upgrade suggestions');
        }
    } catch (error) {
        showError('Error getting upgrade suggestions. Please try again.');
        console.error('Error getting upgrade suggestions:', error);
    }
}

// Get playing tips
async function getPlayingTips() {
    if (!playerData) {
        showError('Please get your profile first');
        return;
    }
    
    const currentDeckName = document.getElementById('deckName').textContent || 'Current Deck';
    
    showLoading();
    
    try {
        const response = await fetch('/api/playing-tips', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                deckName: currentDeckName,
                trophies: playerData.trophies,
                playstyle: playerPreferences.playstyle
            })
        });
        
        if (response.ok) {
            const tipsData = await response.json();
            displayPlayingTips(tipsData);
            hideLoading();
        } else {
            const errorData = await response.json();
            showError(errorData.error || 'Failed to get playing tips');
        }
    } catch (error) {
        showError('Error getting playing tips. Please try again.');
        console.error('Error getting playing tips:', error);
    }
}

// Display playing tips
function displayPlayingTips(tipsData) {
    const tipsContainer = document.getElementById('playingTipsContent');
    
    let tipsHtml = `
        <div class="alert alert-info mb-4">
            <h6 class="fw-bold mb-2">
                <i class="fas fa-user-tie me-2"></i>Your Coach's Strategy Guide
            </h6>
            <p class="mb-0">Here's how to master your deck at ${tipsData.trophyRange.range} level:</p>
        </div>
    `;
    
    tipsHtml += '<div class="row">';
    
    tipsData.tips.forEach((tip, index) => {
        tipsHtml += `
            <div class="col-md-6 mb-3">
                <div class="tip-item">
                    <div class="tip-number">${index + 1}</div>
                    <div class="tip-content">
                        <p class="mb-0">${tip}</p>
                    </div>
                </div>
            </div>
        `;
    });
    
    tipsHtml += '</div>';
    
    // Add matchup advice
    tipsHtml += `
        <div class="mt-4">
            <h6 class="fw-bold mb-3">
                <i class="fas fa-chess me-2"></i>General Matchup Strategy
            </h6>
            <div class="alert alert-light">
                <p class="mb-2"><strong>Against Beatdown:</strong> Apply constant pressure and don't let them build big pushes</p>
                <p class="mb-2"><strong>Against Control:</strong> Force them to use their defensive cards, then capitalize</p>
                <p class="mb-2"><strong>Against Cycle:</strong> Disrupt their cycle timing and defend efficiently</p>
                <p class="mb-0"><strong>Against Siege:</strong> Rush the opposite lane when they place their building</p>
            </div>
        </div>
    `;
    
    tipsContainer.innerHTML = tipsHtml;
    
    document.getElementById('playingTips').style.display = 'block';
    document.getElementById('playingTips').classList.add('slide-up');
}

// Display upgrade suggestions
function displayUpgradeSuggestion(upgradeData) {
    const upgradeList = document.getElementById('upgradeList');
    upgradeList.innerHTML = '';
    
    if (upgradeData.recommendations.length === 0) {
        upgradeList.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                <strong>Great!</strong> Your cards are well-leveled for your current trophy range.
            </div>
        `;
    } else {
        // Add trophy range info
        const trophyInfo = upgradeData.trophyRange;
        upgradeList.innerHTML = `
            <div class="alert alert-info mb-4">
                <i class="fas fa-info-circle me-2"></i>
                <strong>Trophy Range Analysis:</strong> You're in ${trophyInfo.range}. 
                Recommended card levels: ${trophyInfo.recommendedCardLevel}
            </div>
        `;
        
        upgradeData.recommendations.forEach((recommendation, index) => {
            const priorityClass = recommendation.priority > 15 ? 'priority-high' : 
                                 recommendation.priority > 8 ? 'priority-medium' : 'priority-low';
            const priorityText = recommendation.priority > 15 ? 'High' : 
                                 recommendation.priority > 8 ? 'Medium' : 'Low';
            
            const upgradeElement = document.createElement('div');
            upgradeElement.className = 'upgrade-item';
            upgradeElement.innerHTML = `
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center">
                        <div class="card-icon me-3" style="width: 40px; height: 40px; font-size: 16px;">
                            <i class="${getCardIcon(recommendation.card)}"></i>
                        </div>
                        <div>
                            <h6 class="mb-1 fw-bold">${recommendation.card}</h6>
                            <small class="text-muted">Appears in ${recommendation.appearsInDecks} meta deck${recommendation.appearsInDecks > 1 ? 's' : ''}</small>
                        </div>
                    </div>
                    <span class="upgrade-priority ${priorityClass}">${priorityText} Priority</span>
                </div>
                <div class="row">
                    <div class="col-md-3">
                        <small class="text-muted d-block">Current Level</small>
                        <strong class="text-primary">${recommendation.currentLevel}</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Recommended Level</small>
                        <strong class="text-success">${recommendation.recommendedLevel}</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Levels Needed</small>
                        <strong class="text-warning">${recommendation.levelDeficit}</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Avg Win Rate</small>
                        <strong class="text-info">${recommendation.averageWinRate.toFixed(1)}%</strong>
                    </div>
                </div>
            `;
            upgradeList.appendChild(upgradeElement);
        });
    }
    
    document.getElementById('upgradeSuggestion').style.display = 'block';
    document.getElementById('upgradeSuggestion').classList.add('fade-in');
}

// Hide sections when getting new profile
function resetSections() {
    document.getElementById('playerProfile').style.display = 'none';
    document.getElementById('actionButtons').style.display = 'none';
    document.getElementById('deckSuggestion').style.display = 'none';
    document.getElementById('upgradeSuggestion').style.display = 'none';
    document.getElementById('currentDeck').style.display = 'none';
    hideError();
}

// Add input validation styling
playerTagInput.addEventListener('input', function() {
    const value = this.value.trim();
    if (value && !validatePlayerTag(value)) {
        this.classList.add('is-invalid');
    } else {
        this.classList.remove('is-invalid');
    }
});
