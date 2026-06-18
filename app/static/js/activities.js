(function () {
    const root = document.getElementById("activities-app");
    if (!root || !window.Edupets) {
        return;
    }

    const username = root.dataset.username;
    const serverState = Edupets.readJsonScript("activity-data");
    let state = Edupets.mergeServerState(username, serverState);
    state = Edupets.applyElapsedDecay(state);
    Edupets.saveState(username, state);

    const modules = [
        { id: "sumas", label: "Sumas", symbol: "+" },
        { id: "restas", label: "Restas", symbol: "-" },
        { id: "multiplicacion", label: "Multiplicación", symbol: "×" },
        { id: "division", label: "División", symbol: "÷" },
    ];
    const totalLevels = 5;
    const questionsPerLevel = 5;
    const levelMap = document.getElementById("level-map");
    const modal = document.getElementById("exercise-modal");
    const titleNode = document.getElementById("exercise-title");
    const livesRow = document.getElementById("lives-row");
    const progressNode = document.getElementById("exercise-progress");
    const questionNode = document.getElementById("question-text");
    const optionsNode = document.getElementById("answer-options");
    const feedbackNode = document.getElementById("exercise-feedback");
    const closeButton = document.getElementById("close-exercise");
    const coinsNode = root.querySelector('[data-role="coins"]');
    let current = null;

    function completedLevels(moduleId) {
        const completed = state.progress?.completed?.[moduleId];
        return Array.isArray(completed) ? completed.map(Number) : [];
    }

    function isUnlocked(moduleId, level) {
        return level === 1 || completedLevels(moduleId).includes(level - 1);
    }

    function renderCoins() {
        if (coinsNode) {
            coinsNode.textContent = state.coins;
        }
    }

    function renderMap() {
        renderCoins();
        levelMap.innerHTML = "";
        modules.forEach((module) => {
            const lane = document.createElement("section");
            lane.className = "module-lane";
            const levels = completedLevels(module.id);
            lane.innerHTML = `
                <div class="module-heading">
                    <h2>${module.label}</h2>
                    <strong>${levels.length}/${totalLevels}</strong>
                </div>
                <div class="level-buttons"></div>
            `;

            const buttons = lane.querySelector(".level-buttons");
            for (let level = 1; level <= totalLevels; level += 1) {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "level-button";
                button.textContent = `${module.symbol}${level}`;
                button.disabled = !isUnlocked(module.id, level);
                if (levels.includes(level)) {
                    button.classList.add("completed");
                }
                button.addEventListener("click", () => startLevel(module, level));
                buttons.appendChild(button);
            }
            levelMap.appendChild(lane);
        });
    }

    function randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function shuffle(values) {
        return values
            .map((value) => ({ value, sort: Math.random() }))
            .sort((a, b) => a.sort - b.sort)
            .map((entry) => entry.value);
    }

    function makeQuestion(moduleId) {
        let a;
        let b;
        let answer;
        let text;

        if (moduleId === "sumas") {
            a = randomInt(1, 14);
            b = randomInt(1, 14);
            answer = a + b;
            text = `${a} + ${b} = ?`;
        } else if (moduleId === "restas") {
            a = randomInt(6, 24);
            b = randomInt(1, a);
            answer = a - b;
            text = `${a} - ${b} = ?`;
        } else if (moduleId === "multiplicacion") {
            a = randomInt(2, 10);
            b = randomInt(2, 10);
            answer = a * b;
            text = `${a} × ${b} = ?`;
        } else {
            b = randomInt(2, 10);
            answer = randomInt(2, 10);
            a = b * answer;
            text = `${a} ÷ ${b} = ?`;
        }

        const options = new Set([answer]);
        while (options.size < 3) {
            const offset = randomInt(-10, 10) || 3;
            const wrong = Math.max(0, answer + offset);
            if (wrong !== answer) {
                options.add(wrong);
            }
        }

        return { text, answer, options: shuffle([...options]) };
    }

    function renderLives() {
        livesRow.innerHTML = "";
        for (let index = 0; index < 3; index += 1) {
            const img = document.createElement("img");
            img.src = index < current.lives ? "/static/images/vida.png" : "/static/images/vidamenos.png";
            img.alt = index < current.lives ? "Vida" : "Vida perdida";
            livesRow.appendChild(img);
        }
    }

    function renderExercise() {
        renderLives();
        progressNode.innerHTML = `<span style="--progress: ${(current.correct / questionsPerLevel) * 100}%"></span>`;
        const question = makeQuestion(current.module.id);
        current.answer = question.answer;
        titleNode.textContent = `${current.module.label} · Nivel ${current.level}`;
        questionNode.textContent = question.text;
        feedbackNode.textContent = "";
        optionsNode.innerHTML = "";
        question.options.forEach((option) => {
            const button = document.createElement("button");
            button.type = "button";
            button.textContent = option;
            button.addEventListener("click", () => submitAnswer(option));
            optionsNode.appendChild(button);
        });
    }

    function startLevel(module, level) {
        current = {
            module,
            level,
            lives: 3,
            correct: 0,
            answer: null,
        };
        modal.hidden = false;
        renderExercise();
    }

    function disableAnswers() {
        optionsNode.querySelectorAll("button").forEach((button) => {
            button.disabled = true;
        });
    }

    async function completeLevel() {
        disableAnswers();
        feedbackNode.textContent = "Completado";
        try {
            const payload = await Edupets.api("/api/activities/complete", {
                method: "POST",
                body: JSON.stringify({
                    csrf_token: Edupets.csrfToken,
                    module: current.module.id,
                    level: current.level,
                    correct_count: questionsPerLevel,
                }),
            });
            state = Edupets.applyServerSnapshot(username, payload.user);
            feedbackNode.textContent = `+${payload.reward} monedas`;
            renderMap();
            setTimeout(() => {
                modal.hidden = true;
                current = null;
            }, 900);
        } catch (error) {
            feedbackNode.textContent = error.message;
        }
    }

    function submitAnswer(value) {
        if (!current) {
            return;
        }

        if (value === current.answer) {
            current.correct += 1;
            if (current.correct >= questionsPerLevel) {
                completeLevel();
                return;
            }
            feedbackNode.textContent = "Correcto";
            setTimeout(renderExercise, 360);
            return;
        }

        current.lives -= 1;
        renderLives();
        if (current.lives <= 0) {
            disableAnswers();
            feedbackNode.textContent = "Sin vidas";
            setTimeout(() => {
                window.location.href = "/pet";
            }, 1000);
            return;
        }
        feedbackNode.textContent = "Intenta otra";
    }

    closeButton.addEventListener("click", () => {
        modal.hidden = true;
        current = null;
    });

    renderMap();
})();
