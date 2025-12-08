// Wheel of Fortune Game with Setup Screens and AI Players
class WheelOfFortuneGame {
    constructor() {
        this.currentScreen = 'setup';
        this.gameState = {
            players: [],
            currentPlayerIndex: 0,
            puzzle: null,
            revealedLetters: [],
            usedLetters: [],
            wheelValue: 0,
            gamePhase: 'setup', // setup, naming, playing, ended
            currentRound: 1,
            totalRounds: 3,
            roundScores: [] // Track scores for each round
        };
        this.setupConfig = {
            humanPlayers: 1,
            aiPlayers: 2,
            aiStrategy: 'morse',
            totalRounds: 3
        };
        this.backendUrl = window.location.origin.replace(':12000', ':12001'); // Backend on port 12001
        
        // Initialize the new puzzle manager
        this.puzzleManager = new PuzzleManager();
        
        // Initialize money optimizer
        this.moneyOptimizer = new MoneyOptimizer();
        
        // Wheel configuration (24 sections, matching create_accurate_wheel.py)
        // 0 = LOSE TURN, -1 = BANKRUPT
        this.wheelSections = [0, -1, 500, 550, 600, 650, 700, 750, 800, 850, 900, -1, 
                             500, 550, 600, 650, 700, 750, 800, 850, 900, 500, 550, 600];
        this.currentWheelRotation = 0; // Track current wheel rotation
        
        // Log puzzle statistics
        console.log(`Puzzle System Loaded:`);
        console.log(`- Total puzzles: ${this.puzzleManager.getTotalPuzzleCount()}`);
        console.log(`- Categories: ${this.puzzleManager.getCategories().join(', ')}`);
        this.puzzleManager.getCategories().forEach(category => {
            console.log(`  - ${category}: ${this.puzzleManager.getCategoryPuzzleCount(category)} puzzles`);
        });
        
        this.init();
    }

    init() {
        this.bindSetupEvents();
        this.bindNamingEvents();
        this.bindGameEvents();
        this.updateTotalPlayers();
    }

    // Setup Screen Methods
    bindSetupEvents() {
        const continueBtn = document.getElementById('continueToNaming');
        if (continueBtn) {
            continueBtn.addEventListener('click', () => this.proceedToNaming());
        }
        
        // Round selection buttons
        const roundButtons = document.querySelectorAll('.round-btn');
        roundButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Remove active class from all buttons
                roundButtons.forEach(b => b.classList.remove('active'));
                // Add active class to clicked button
                e.target.classList.add('active');
                // Update configuration
                this.setupConfig.totalRounds = parseInt(e.target.dataset.rounds);
                this.gameState.totalRounds = this.setupConfig.totalRounds;
            });
        });
    }

    changePlayerCount(type, delta) {
        if (type === 'human') {
            this.setupConfig.humanPlayers = Math.max(0, Math.min(6, this.setupConfig.humanPlayers + delta));
            document.getElementById('humanCount').textContent = this.setupConfig.humanPlayers;
        } else if (type === 'ai') {
            this.setupConfig.aiPlayers = Math.max(0, Math.min(6, this.setupConfig.aiPlayers + delta));
            document.getElementById('aiCount').textContent = this.setupConfig.aiPlayers;
        }
        
        this.updateTotalPlayers();
        this.updateCounterButtons();
    }

    updateTotalPlayers() {
        const total = this.setupConfig.humanPlayers + this.setupConfig.aiPlayers;
        document.getElementById('totalPlayers').textContent = total;
        
        // Enable/disable continue button
        const continueBtn = document.getElementById('continueToNaming');
        if (continueBtn) {
            continueBtn.disabled = total < 1 || total > 6;
        }
    }

    updateCounterButtons() {
        const total = this.setupConfig.humanPlayers + this.setupConfig.aiPlayers;
        
        // Update human counter buttons
        const humanMinusBtn = document.querySelector('.player-type-section:first-child .counter-btn:first-child');
        const humanPlusBtn = document.querySelector('.player-type-section:first-child .counter-btn:last-child');
        if (humanMinusBtn) humanMinusBtn.disabled = this.setupConfig.humanPlayers <= 0;
        if (humanPlusBtn) humanPlusBtn.disabled = total >= 6;
        
        // Update AI counter buttons
        const aiMinusBtn = document.querySelector('.player-type-section:last-child .counter-btn:first-child');
        const aiPlusBtn = document.querySelector('.player-type-section:last-child .counter-btn:last-child');
        if (aiMinusBtn) aiMinusBtn.disabled = this.setupConfig.aiPlayers <= 0;
        if (aiPlusBtn) aiPlusBtn.disabled = total >= 6;
    }

    proceedToNaming() {
        this.setupConfig.aiStrategy = document.getElementById('aiStrategy').value;
        this.showScreen('naming');
        this.generateNamingInputs();
    }

    // Naming Screen Methods
    bindNamingEvents() {
        const startBtn = document.getElementById('startGame');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startGame());
        }
    }

    generateNamingInputs() {
        const container = document.getElementById('namingInputs');
        container.innerHTML = '';

        // Generate inputs for human players
        for (let i = 0; i < this.setupConfig.humanPlayers; i++) {
            const div = document.createElement('div');
            div.className = 'player-naming';
            div.innerHTML = `
                <label for="human${i}">Human ${i + 1}:</label>
                <input type="text" id="human${i}" placeholder="Enter player name" maxlength="20">
            `;
            container.appendChild(div);
        }

        // Generate displays for AI players
        for (let i = 0; i < this.setupConfig.aiPlayers; i++) {
            const div = document.createElement('div');
            div.className = 'player-naming';
            div.innerHTML = `
                <label>AI ${i + 1}:</label>
                <span class="ai-indicator">Computer Player (${this.setupConfig.aiStrategy})</span>
            `;
            container.appendChild(div);
        }
    }

    async startGame() {
        // Collect player names
        this.gameState.players = [];
        
        // Add human players
        for (let i = 0; i < this.setupConfig.humanPlayers; i++) {
            const nameInput = document.getElementById(`human${i}`);
            const name = nameInput.value.trim() || `Player ${i + 1}`;
            this.gameState.players.push({
                name: name,
                type: 'human',
                totalScore: 0,
                roundScore: 0,
                isActive: false
            });
        }

        // Add AI players
        for (let i = 0; i < this.setupConfig.aiPlayers; i++) {
            this.gameState.players.push({
                name: `AI ${i + 1}`,
                type: 'ai',
                strategy: this.setupConfig.aiStrategy,
                totalScore: 0,
                roundScore: 0,
                isActive: false
            });
        }

        // Set first player as active
        if (this.gameState.players.length > 0) {
            this.gameState.players[0].isActive = true;
        }

        this.gameState.gamePhase = 'playing';
        this.showScreen('game');
        await this.initializeGame();
    }

    // Game Screen Methods
    bindGameEvents() {
        // Spin button
        const spinBtn = document.getElementById('spinButton');
        if (spinBtn) {
            spinBtn.addEventListener('click', () => this.spinWheel());
        }

        // Guess button
        const guessBtn = document.getElementById('guessButton');
        if (guessBtn) {
            guessBtn.addEventListener('click', () => this.guessLetter());
        }

        // Solve button
        const solveBtn = document.getElementById('solveButton');
        if (solveBtn) {
            solveBtn.addEventListener('click', () => this.solvePuzzle());
        }

        // Buy vowel button
        const vowelBtn = document.getElementById('buyVowelButton');
        if (vowelBtn) {
            vowelBtn.addEventListener('click', () => this.buyVowel());
        }

        // New game button
        const newGameBtn = document.getElementById('newGameButton');
        if (newGameBtn) {
            newGameBtn.addEventListener('click', () => this.newGame());
        }

        // Enter key handlers
        const guessInput = document.getElementById('guessInput');
        if (guessInput) {
            guessInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.guessLetter();
            });
        }

        const phraseInput = document.getElementById('phraseInput');
        if (phraseInput) {
            phraseInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.solvePuzzle();
            });
        }
    }

    initializeGame() {
        // Load a random puzzle using the new puzzle manager
        this.gameState.puzzle = this.puzzleManager.getRandomPuzzle();
        this.gameState.revealedLetters = this.gameState.puzzle.phrase.split('').map(char => 
            char === ' ' ? ' ' : '_'
        );
        this.gameState.usedLetters = [];
        
        this.renderPuzzle();
        this.renderPlayers();
        this.updateRoundDisplay();
        this.updateGameMessage(`Game started! Category: ${this.gameState.puzzle.category}. Auto-spinning wheel...`);
        
        // Auto-spin for all players at game start
        const currentPlayer = this.getCurrentPlayer();
        setTimeout(() => {
            if (currentPlayer.type === 'ai') {
                this.makeAIMove();
            } else {
                this.spinWheel();
            }
        }, 1000);
    }

    renderPuzzle() {
        const board = document.getElementById('puzzleBoard');
        const category = document.getElementById('category');
        
        if (category && this.gameState.puzzle) {
            category.textContent = this.gameState.puzzle.category;
        }
        
        if (!board || !this.gameState.puzzle) return;
        
        board.innerHTML = '';
        
        const words = this.gameState.puzzle.phrase.split(' ');
        words.forEach((word, wordIndex) => {
            const row = document.createElement('div');
            row.className = 'puzzle-row';
            
            for (let i = 0; i < word.length; i++) {
                const letterBox = document.createElement('div');
                letterBox.className = 'letter-box';
                
                const globalIndex = this.getGlobalLetterIndex(wordIndex, i);
                const letter = this.gameState.revealedLetters[globalIndex];
                
                if (letter !== '_') {
                    letterBox.textContent = letter;
                    letterBox.classList.add('revealed');
                }
                
                row.appendChild(letterBox);
            }
            
            board.appendChild(row);
            
            // Add space between words (except after last word)
            if (wordIndex < words.length - 1) {
                const spaceRow = document.createElement('div');
                spaceRow.className = 'puzzle-row';
                const spaceBox = document.createElement('div');
                spaceBox.className = 'letter-box space';
                spaceRow.appendChild(spaceBox);
                board.appendChild(spaceRow);
            }
        });
    }

    getGlobalLetterIndex(wordIndex, letterIndex) {
        let index = 0;
        const words = this.gameState.puzzle.phrase.split(' ');
        
        for (let i = 0; i < wordIndex; i++) {
            index += words[i].length + 1; // +1 for space
        }
        
        return index + letterIndex;
    }

    renderPlayers() {
        const container = document.getElementById('playerScores');
        if (!container) return;
        
        container.innerHTML = '';
        
        this.gameState.players.forEach((player, index) => {
            const playerDiv = document.createElement('div');
            playerDiv.className = `player ${player.isActive ? 'active' : ''}`;
            playerDiv.id = `player${index + 1}`;
            
            const nameDiv = document.createElement('div');
            nameDiv.className = 'player-name';
            nameDiv.innerHTML = `${player.name}${player.type === 'ai' ? '<span class="ai-badge">AI</span>' : ''}`;
            
            const scoreDiv = document.createElement('div');
            scoreDiv.className = 'player-score';
            scoreDiv.textContent = `$${player.totalScore}`;
            
            const roundScoreDiv = document.createElement('div');
            roundScoreDiv.className = 'round-score';
            if (player.roundScore > 0) {
                roundScoreDiv.textContent = `(+$${player.roundScore})`;
            }
            
            playerDiv.appendChild(nameDiv);
            playerDiv.appendChild(scoreDiv);
            playerDiv.appendChild(roundScoreDiv);
            
            container.appendChild(playerDiv);
        });
        
        // Update strategy advisor for human players
        this.updateStrategyAdvisor();
    }

    updateRoundDisplay() {
        const roundCounter = document.getElementById('roundCounter');
        if (roundCounter) {
            roundCounter.textContent = `Round ${this.gameState.currentRound} of ${this.gameState.totalRounds}`;
        }
    }

    getCurrentPlayer() {
        return this.gameState.players[this.gameState.currentPlayerIndex];
    }

    updateStrategyAdvisor() {
        // Only show strategy advisor during active gameplay and for human players
        if (this.gameState.gamePhase !== 'playing' || !this.gameState.puzzle) {
            return;
        }

        const currentPlayer = this.getCurrentPlayer();
        if (!currentPlayer || currentPlayer.type !== 'human') {
            return;
        }

        // Prepare game state for optimizer
        const opponentScores = this.gameState.players
            .filter(p => p !== currentPlayer)
            .map(p => p.totalScore + p.roundScore);

        const gameStateForOptimizer = {
            currentMoney: currentPlayer.roundScore,
            revealedLetters: this.gameState.revealedLetters,
            usedLetters: this.gameState.usedLetters,
            opponentScores: opponentScores,
            roundsRemaining: this.gameState.totalRounds - this.gameState.currentRound + 1,
            category: this.gameState.puzzle.category
        };

        // Get optimal strategy
        const strategy = this.moneyOptimizer.getOptimalStrategy(gameStateForOptimizer);
        const advice = this.moneyOptimizer.formatAdvice(strategy);

        // Update UI elements
        this.updateStrategyUI(advice, strategy);
    }

    updateStrategyUI(advice, strategy) {
        // Update recommendation action
        const actionElement = document.getElementById('recommendedAction');
        if (actionElement) {
            let actionText = advice.action;
            if (actionText === 'BUY_VOWEL') actionText = 'BUY VOWEL';
            actionElement.textContent = actionText;
            
            // Color code the recommendation
            actionElement.className = 'recommendation-action';
            if (actionText === 'SOLVE') {
                actionElement.style.color = '#00ff00'; // Green for solve
            } else if (actionText === 'BUY VOWEL') {
                actionElement.style.color = '#ffaa00'; // Orange for vowel
            } else {
                actionElement.style.color = '#ffd700'; // Gold for spin
            }
        }

        // Update confidence level
        const confidenceElement = document.getElementById('confidenceLevel');
        if (confidenceElement) {
            const expectedValue = strategy.analysis.spin.expectedValue;
            let confidence = 'Medium Confidence';
            if (Math.abs(expectedValue) > 200) {
                confidence = 'High Confidence';
            } else if (Math.abs(expectedValue) < 50) {
                confidence = 'Low Confidence';
            }
            confidenceElement.textContent = confidence;
        }

        // Update reasoning
        const reasoningList = document.getElementById('reasoningList');
        if (reasoningList) {
            reasoningList.innerHTML = '';
            advice.reasoning.forEach(reason => {
                const li = document.createElement('li');
                li.textContent = reason;
                reasoningList.appendChild(li);
            });
        }

        // Update wheel statistics
        const bankruptChance = document.getElementById('bankruptChance');
        if (bankruptChance) {
            bankruptChance.textContent = advice.wheelStats.bankruptChance;
        }

        const loseTurnChance = document.getElementById('loseTurnChance');
        if (loseTurnChance) {
            loseTurnChance.textContent = advice.wheelStats.loseTurnChance;
        }

        const expectedSpinValue = document.getElementById('expectedSpinValue');
        if (expectedSpinValue) {
            expectedSpinValue.textContent = advice.wheelStats.expectedSpinValue;
        }

        // Update letter suggestions
        const suggestedConsonants = document.getElementById('suggestedConsonants');
        if (suggestedConsonants) {
            suggestedConsonants.innerHTML = '';
            advice.letterSuggestions.consonants.forEach(consonant => {
                const span = document.createElement('span');
                span.className = 'letter-suggestion';
                span.textContent = consonant;
                suggestedConsonants.appendChild(span);
            });
        }

        const suggestedVowel = document.getElementById('suggestedVowel');
        if (suggestedVowel) {
            suggestedVowel.textContent = advice.letterSuggestions.vowel;
        }
    }

    // Calculate the rotation angle needed to land on a specific wheel section
    calculateWheelRotation(targetValue) {
        // Find all sections with the target value
        const matchingSections = [];
        this.wheelSections.forEach((value, index) => {
            if (value === targetValue) {
                matchingSections.push(index);
            }
        });
        
        if (matchingSections.length === 0) {
            console.error('Target value not found on wheel:', targetValue);
            return 1800; // Default fallback
        }
        
        // Pick a random matching section
        const targetSection = matchingSections[Math.floor(Math.random() * matchingSections.length)];
        
        // Calculate angle for this section (24 sections = 15 degrees each)
        const degreesPerSection = 360 / this.wheelSections.length; // 15 degrees
        
        // Simple approach: Section 0 is at the top, sections go clockwise
        // To get target section to the top (pointer), rotate counter-clockwise
        const sectionAngle = targetSection * degreesPerSection;
        const targetAngle = -sectionAngle;
        
        // Add multiple full rotations for dramatic effect (4-6 full spins)
        const fullRotations = 4 + Math.random() * 2; // 4-6 rotations
        const finalRotation = (fullRotations * 360) + targetAngle;
        
        console.log(`Target: ${targetValue}, Section: ${targetSection}, Angle: ${sectionAngle}°, Final rotation: ${finalRotation}°`);
        
        return finalRotation;
    }

    // Get a random wheel result based on realistic probabilities
    getRandomWheelResult() {
        // Create weighted array (more money values, fewer special spaces)
        const weightedSections = [];
        
        this.wheelSections.forEach((value, index) => {
            if (value === -1) { // BANKRUPT - lower probability
                weightedSections.push(value);
            } else if (value === 0) { // LOSE TURN - lower probability  
                weightedSections.push(value);
            } else { // Money values - higher probability
                weightedSections.push(value);
                weightedSections.push(value); // Add twice for higher probability
            }
        });
        
        const randomValue = weightedSections[Math.floor(Math.random() * weightedSections.length)];
        
        // Check for hidden lucky sections (rare chance for higher amounts)
        let finalValue = randomValue;
        let isLucky = false;
        
        if (randomValue > 0) { // Only for money values
            const luckRoll = Math.random();
            if (luckRoll < 0.05) { // 5% chance for lucky amounts
                const luckyAmounts = [1500, 2000, 2500, 3000, 3500, 5000];
                finalValue = luckyAmounts[Math.floor(Math.random() * luckyAmounts.length)];
                isLucky = true;
            }
        }
        
        return {
            type: randomValue === 0 ? 'lose_turn' : randomValue === -1 ? 'bankrupt' : 'money',
            value: finalValue > 0 ? finalValue : 0,
            wheelValue: randomValue, // The value that corresponds to the wheel section
            isLucky: isLucky,
            message: randomValue === 0 ? 'Lose a Turn!' : 
                     randomValue === -1 ? 'Bankrupt!' : 
                     isLucky ? `LUCKY SPIN! $${finalValue}` : `$${finalValue}`
        };
    }

    async spinWheel() {
        const spinBtn = document.getElementById('spinButton');
        const wheelImg = document.getElementById('wheelImage');
        
        if (!spinBtn || !wheelImg) return;
        
        spinBtn.disabled = true;
        
        // Get random result first
        const result = this.getRandomWheelResult();
        
        // Calculate the exact rotation needed for this result (use wheelValue for accurate positioning)
        const targetRotation = this.calculateWheelRotation(
            result.type === 'lose_turn' ? 0 : 
            result.type === 'bankrupt' ? -1 : 
            result.wheelValue || result.value
        );
        
        // Apply the calculated rotation with animation
        wheelImg.style.transition = 'transform 3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        wheelImg.style.transform = `rotate(${this.currentWheelRotation + targetRotation}deg)`;
        
        // Update current rotation for next spin
        this.currentWheelRotation += targetRotation;
        
        // Handle the result after animation completes
        setTimeout(() => {
            this.handleSpinResult(result);
            spinBtn.disabled = false;
        }, 3000);
    }

    handleSpinResult(result) {
        const wheelResult = document.getElementById('wheelResult');
        if (wheelResult) {
            // Clear previous classes
            wheelResult.className = 'wheel-result';
            wheelResult.textContent = result.message;
            
            // Add appropriate class for visual effect
            if (result.type === 'bankrupt') {
                wheelResult.classList.add('bankrupt');
                wheelResult.textContent = '💸 BANKRUPT! 💸';
            } else if (result.type === 'lose_turn') {
                wheelResult.classList.add('lose-turn');
                wheelResult.textContent = '⏭️ LOSE A TURN! ⏭️';
            } else if (result.type === 'money') {
                wheelResult.classList.add('money');
                wheelResult.textContent = `💰 $${result.value} 💰`;
            }
            
            // Remove the class after animation completes
            setTimeout(() => {
                if (wheelResult.classList.contains('bankrupt') || 
                    wheelResult.classList.contains('lose-turn') || 
                    wheelResult.classList.contains('money')) {
                    wheelResult.className = 'wheel-result';
                }
            }, 3000);
        }
        
        const currentPlayer = this.getCurrentPlayer();
        
        if (result.type === 'bankrupt') {
            currentPlayer.roundScore = 0;
            this.updateGameMessage(`💸 ${currentPlayer.name} went BANKRUPT! All round earnings lost. Turn passes to next player.`);
            setTimeout(() => this.nextPlayer(), 2500); // Give time to see the result
        } else if (result.type === 'lose_turn') {
            this.updateGameMessage(`⏭️ ${currentPlayer.name} lost their turn! No money lost, but turn passes to next player.`);
            setTimeout(() => this.nextPlayer(), 2500); // Give time to see the result
        } else {
            this.gameState.wheelValue = result.value;
            this.updateGameMessage(`💰 ${currentPlayer.name} spun $${result.value}! Guess a consonant to earn money.`);
            
            // Enable guess input for human players
            if (currentPlayer.type === 'human') {
                const guessInput = document.getElementById('guessInput');
                if (guessInput) {
                    guessInput.focus();
                }
            } else {
                // AI player makes move
                setTimeout(() => this.makeAIMove(), 1000);
            }
        }
        
        this.renderPlayers();
    }

    async guessLetter() {
        const input = document.getElementById('guessInput');
        if (!input) return;
        
        const letter = input.value.toUpperCase().trim();
        input.value = '';
        
        if (!letter || letter.length !== 1 || !/[A-Z]/.test(letter)) {
            this.updateGameMessage('Please enter a valid letter.');
            return;
        }
        
        if (this.gameState.usedLetters.includes(letter)) {
            this.updateGameMessage('That letter has already been used.');
            return;
        }
        
        const vowels = 'AEIOU';
        if (vowels.includes(letter)) {
            this.updateGameMessage('Please spin the wheel first, then guess a consonant.');
            return;
        }
        
        this.processLetterGuess(letter);
    }

    processLetterGuess(letter) {
        this.gameState.usedLetters.push(letter);
        const currentPlayer = this.getCurrentPlayer();
        const vowels = 'AEIOU';
        const isVowel = vowels.includes(letter);
        
        // Check if letter is in puzzle
        const letterCount = (this.gameState.puzzle.phrase.match(new RegExp(letter, 'g')) || []).length;
        
        if (letterCount > 0) {
            // Reveal letters
            for (let i = 0; i < this.gameState.puzzle.phrase.length; i++) {
                if (this.gameState.puzzle.phrase[i] === letter) {
                    this.gameState.revealedLetters[i] = letter;
                }
            }
            
            // Add money to round score (only for consonants, not vowels)
            if (isVowel) {
                // Vowels don't earn money, they cost $250 (already deducted in buyVowel)
                this.updateGameMessage(`Great! There ${letterCount === 1 ? 'is' : 'are'} ${letterCount} ${letter}'s. (Vowels don't earn money)`);
            } else {
                // Consonants earn money based on wheel value
                const earned = letterCount * this.gameState.wheelValue;
                currentPlayer.roundScore += earned;
                this.updateGameMessage(`Great! There ${letterCount === 1 ? 'is' : 'are'} ${letterCount} ${letter}'s. You earned $${earned}!`);
            }
            
            // Check if puzzle is solved
            if (!this.gameState.revealedLetters.includes('_')) {
                this.solvePuzzleSuccess(currentPlayer);
                return;
            }
            
        } else {
            if (isVowel) {
                this.updateGameMessage(`Sorry, no ${letter}'s in the puzzle. (You still paid $250 for the vowel) Your turn is over.`);
            } else {
                this.updateGameMessage(`Sorry, no ${letter}'s in the puzzle. Your turn is over.`);
            }
            // Give time to read the message before moving to next player
            setTimeout(() => this.nextPlayer(), 2500);
        }
        
        this.renderPuzzle();
        this.renderPlayers();
        this.renderUsedLetters();
        
        // If current player is AI and it's still their turn, make next move
        if (letterCount > 0 && this.getCurrentPlayer().type === 'ai') {
            setTimeout(() => this.makeAIMove(), 1500);
        }
    }

    async buyVowel() {
        const currentPlayer = this.getCurrentPlayer();
        
        if (currentPlayer.roundScore < 250) {
            this.updateGameMessage('You need at least $250 to buy a vowel.');
            return;
        }
        
        const vowel = prompt('Which vowel would you like to buy? (A, E, I, O, U)');
        if (!vowel) return;
        
        const letter = vowel.toUpperCase().trim();
        const vowels = 'AEIOU';
        
        if (!vowels.includes(letter)) {
            this.updateGameMessage('Please enter a valid vowel (A, E, I, O, U).');
            return;
        }
        
        if (this.gameState.usedLetters.includes(letter)) {
            this.updateGameMessage('That vowel has already been used.');
            return;
        }
        
        currentPlayer.roundScore -= 250;
        this.processLetterGuess(letter);
    }

    solvePuzzle() {
        const input = document.getElementById('phraseInput');
        if (!input) return;
        
        const guess = input.value.toUpperCase().trim();
        input.value = '';
        
        if (!guess) {
            this.updateGameMessage('Please enter your solution.');
            return;
        }
        
        const currentPlayer = this.getCurrentPlayer();
        
        if (guess === this.gameState.puzzle.phrase) {
            this.solvePuzzleSuccess(currentPlayer);
        } else {
            this.updateGameMessage(`Sorry, "${guess}" is not correct.`);
            this.nextPlayer();
        }
    }

    solvePuzzleSuccess(player) {
        player.totalScore += player.roundScore;
        this.updateGameMessage(`🎉 ${player.name} solved the puzzle: "${this.gameState.puzzle.phrase}" and won $${player.roundScore}!`);
        
        // Reset for new round
        setTimeout(() => {
            this.newRound();
        }, 3000);
    }

    async makeAIMove() {
        const currentPlayer = this.getCurrentPlayer();
        if (currentPlayer.type !== 'ai') return;
        
        try {
            const response = await fetch(`${this.backendUrl}/api/ai/move`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    strategy: currentPlayer.strategy,
                    revealed_letters: this.gameState.revealedLetters,
                    used_letters: this.gameState.usedLetters,
                    current_money: currentPlayer.roundScore,
                    puzzle_category: this.gameState.puzzle.category
                })
            });
            
            const move = await response.json();
            
            if (move.action === 'buy_vowel') {
                if (currentPlayer.roundScore >= 250) {
                    currentPlayer.roundScore -= 250;
                    this.updateGameMessage(`${currentPlayer.name} bought vowel ${move.letter}.`);
                    this.processLetterGuess(move.letter);
                } else {
                    // Fallback to spinning
                    this.updateGameMessage(`${currentPlayer.name} spins the wheel.`);
                    setTimeout(() => this.spinWheel(), 1000);
                }
            } else if (move.action === 'guess_consonant') {
                if (this.gameState.wheelValue > 0) {
                    this.updateGameMessage(`${currentPlayer.name} guesses ${move.letter}.`);
                    this.processLetterGuess(move.letter);
                } else {
                    // Need to spin first
                    this.updateGameMessage(`${currentPlayer.name} spins the wheel.`);
                    setTimeout(() => this.spinWheel(), 1000);
                }
            } else {
                // Try to solve or spin
                this.updateGameMessage(`${currentPlayer.name} spins the wheel.`);
                setTimeout(() => this.spinWheel(), 1000);
            }
            
        } catch (error) {
            console.error('Error getting AI move:', error);
            // Fallback AI logic
            this.makeSimpleAIMove();
        }
    }

    makeSimpleAIMove() {
        const currentPlayer = this.getCurrentPlayer();
        const alphabet = "ETAINOSHRDLUCMFWYGPBVKQJXZ"; // Morse frequency
        const vowels = "AEIOU";
        
        // Find next unused letter
        for (const letter of alphabet) {
            if (!this.gameState.usedLetters.includes(letter)) {
                if (vowels.includes(letter)) {
                    if (currentPlayer.roundScore >= 250) {
                        currentPlayer.roundScore -= 250;
                        this.updateGameMessage(`${currentPlayer.name} bought vowel ${letter}.`);
                        this.processLetterGuess(letter);
                        return;
                    }
                } else {
                    if (this.gameState.wheelValue > 0) {
                        this.updateGameMessage(`${currentPlayer.name} guesses ${letter}.`);
                        this.processLetterGuess(letter);
                        return;
                    } else {
                        this.updateGameMessage(`${currentPlayer.name} spins the wheel.`);
                        setTimeout(() => this.spinWheel(), 1000);
                        return;
                    }
                }
            }
        }
        
        // If no letters left, try to solve (placeholder)
        this.updateGameMessage(`${currentPlayer.name} passes.`);
        this.nextPlayer();
    }

    nextPlayer() {
        // Reset wheel value
        this.gameState.wheelValue = 0;
        const wheelResult = document.getElementById('wheelResult');
        if (wheelResult) {
            wheelResult.textContent = 'Click SPIN to start!';
        }
        
        // Move to next player
        this.gameState.players[this.gameState.currentPlayerIndex].isActive = false;
        this.gameState.currentPlayerIndex = (this.gameState.currentPlayerIndex + 1) % this.gameState.players.length;
        this.gameState.players[this.gameState.currentPlayerIndex].isActive = true;
        
        this.renderPlayers();
        
        const currentPlayer = this.getCurrentPlayer();
        this.updateGameMessage(`${currentPlayer.name}'s turn!`);
        
        // Automatic spin failsafe - spin wheel for all players at start of turn
        setTimeout(() => {
            if (currentPlayer.type === 'ai') {
                this.makeAIMove();
            } else {
                // Auto-spin for human players to ensure game flow
                this.updateGameMessage(`${currentPlayer.name}'s turn! Auto-spinning wheel...`);
                setTimeout(() => this.spinWheel(), 1000);
            }
        }, 1500);
    }

    renderUsedLetters() {
        const container = document.getElementById('usedLetters');
        if (!container) return;
        
        container.innerHTML = '';
        
        this.gameState.usedLetters.sort().forEach(letter => {
            const letterSpan = document.createElement('span');
            letterSpan.className = 'used-letter';
            letterSpan.textContent = letter;
            container.appendChild(letterSpan);
        });
    }

    updateGameMessage(message) {
        const messageDiv = document.getElementById('gameMessage');
        if (messageDiv) {
            messageDiv.textContent = message;
        }
    }

    async newRound() {
        // Check if game is complete
        if (this.gameState.currentRound >= this.gameState.totalRounds) {
            this.endGame();
            return;
        }
        
        // Move to next round
        this.gameState.currentRound++;
        
        // Reset round scores but keep total scores
        this.gameState.players.forEach(player => {
            player.roundScore = 0;
        });
        
        // Reset game state for new round
        this.gameState.wheelValue = 0;
        this.gameState.currentPlayerIndex = 0;
        this.gameState.players[0].isActive = true;
        this.gameState.players.forEach((player, index) => {
            player.isActive = index === 0;
        });
        
        // Show round transition message
        this.updateGameMessage(`🎯 Starting Round ${this.gameState.currentRound} of ${this.gameState.totalRounds}!`);
        
        // Load new puzzle and update display
        await this.initializeGame();
        
        // Ensure used letters display is updated
        this.renderUsedLetters();
    }
    
    endGame() {
        // Find winner (highest total score)
        const winner = this.gameState.players.reduce((prev, current) => 
            (prev.totalScore > current.totalScore) ? prev : current
        );
        
        // Show final results
        let resultsMessage = `🏆 GAME COMPLETE! 🏆\n\nWinner: ${winner.name} with $${winner.totalScore}!\n\nFinal Scores:\n`;
        
        // Sort players by score (descending)
        const sortedPlayers = [...this.gameState.players].sort((a, b) => b.totalScore - a.totalScore);
        sortedPlayers.forEach((player, index) => {
            const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '  ';
            resultsMessage += `${medal} ${player.name}: $${player.totalScore}\n`;
        });
        
        this.updateGameMessage(resultsMessage);
        
        // Show new game option after delay
        setTimeout(() => {
            if (confirm('Game Over! Would you like to start a new game?')) {
                this.newGame();
            }
        }, 5000);
    }

    newGame() {
        this.gameState = {
            players: [],
            currentPlayerIndex: 0,
            puzzle: null,
            revealedLetters: [],
            usedLetters: [],
            wheelValue: 0,
            gamePhase: 'setup',
            currentRound: 1,
            totalRounds: 3,
            roundScores: []
        };
        
        this.setupConfig = {
            humanPlayers: 1,
            aiPlayers: 2,
            aiStrategy: 'morse',
            totalRounds: 3
        };
        
        // Reset setup screen values
        document.getElementById('humanCount').textContent = '1';
        document.getElementById('aiCount').textContent = '2';
        document.getElementById('aiStrategy').value = 'morse';
        
        // Reset round selection buttons
        document.querySelectorAll('.round-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.rounds === '3') {
                btn.classList.add('active');
            }
        });
        
        this.showScreen('setup');
        this.updateTotalPlayers();
    }

    showScreen(screenName) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // Show target screen
        const targetScreen = document.getElementById(`${screenName}Screen`);
        if (targetScreen) {
            targetScreen.classList.add('active');
        }
        
        this.currentScreen = screenName;
    }
}

// Global functions for HTML onclick handlers
function changePlayerCount(type, delta) {
    if (window.game) {
        window.game.changePlayerCount(type, delta);
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.game = new WheelOfFortuneGame();
});