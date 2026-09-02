(function () {
    const root = document.getElementById("pet-app");
    if (!root || !window.Edupets) {
        return;
    }

    const username = root.dataset.username;
    const serverState = Edupets.readJsonScript("pet-data");
    let state = Edupets.mergeServerState(username, serverState);
    state = Edupets.applyElapsedDecay(state);
    Edupets.saveState(username, state);

    const statNames = ["happiness", "food", "sleep"];
    const nameInput = document.getElementById("pet-name");
    const statusNode = root.querySelector('[data-role="name-status"]');
    const coinsNode = root.querySelector('[data-role="coins"]');
    const tasksList = document.getElementById("tasks-list");
    let nameTimer = null;
    let syncInFlight = null;
    let lastBeaconAt = 0;

    function renderStats() {
        statNames.forEach((stat) => {
            const orb = root.querySelector(`[data-stat="${stat}"]`);
            const valueNode = root.querySelector(`[data-stat-value="${stat}"]`);
            const value = Edupets.clamp(state[stat]);
            if (orb) {
                orb.style.setProperty("--value", value);
            }
            if (valueNode) {
                valueNode.textContent = `${value}%`;
            }
        });
        if (coinsNode) {
            coinsNode.textContent = state.coins;
        }
        if (nameInput && document.activeElement !== nameInput) {
            nameInput.value = state.pet_name;
        }
        Edupets.updateLogoutFields(username, state);
    }

    function renderTasks() {
        if (!tasksList) {
            return;
        }
        const tasks = state.tasks || {};
        const entries = Object.entries(tasks);
        tasksList.innerHTML = "";

        entries.forEach(([, task]) => {
            const progress = Math.min(task.progress || 0, task.target || 1);
            const target = task.target || 1;
            const row = document.createElement("div");
            row.className = "task-row";
            row.innerHTML = `
                <div class="task-title">
                    <span>${task.label}</span>
                    <span>${progress}/${target}</span>
                </div>
                <div class="task-bar"><span style="--progress: ${(progress / target) * 100}%"></span></div>
            `;
            tasksList.appendChild(row);
        });
    }

    function render() {
        renderStats();
        renderTasks();
        Edupets.saveState(username, state);
    }

    function buildPayload() {
        return {
            csrf_token: Edupets.csrfToken,
            happiness: state.happiness,
            food: state.food,
            sleep: state.sleep,
            pet_name: state.pet_name,
        };
    }

    async function syncNow(useBeacon = false) {
        if (useBeacon) {
            if (Date.now() - lastBeaconAt < 1000) {
                return;
            }
            lastBeaconAt = Date.now();
        } else if (syncInFlight) {
            return syncInFlight;
        }
        state = Edupets.applyElapsedDecay(state);
        Edupets.saveState(username, state);
        const payload = buildPayload();

        if (useBeacon && navigator.sendBeacon) {
            const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
            navigator.sendBeacon("/api/pet/sync", blob);
            return;
        }

        syncInFlight = Edupets.api("/api/pet/sync", {
            method: "POST",
            body: JSON.stringify(payload),
        })
            .then((response) => {
                state = Edupets.applyServerSnapshot(username, response.user);
                render();
            })
            .finally(() => {
                syncInFlight = null;
            });
        return syncInFlight;
    }

    async function saveName() {
        state.pet_name = (nameInput.value || "Mi Mascota").trim().slice(0, 30) || "Mi Mascota";
        Edupets.saveState(username, state);
        if (statusNode) {
            statusNode.textContent = "Guardando";
        }
        try {
            const response = await Edupets.api("/api/pet/name", {
                method: "PATCH",
                body: JSON.stringify({
                    csrf_token: Edupets.csrfToken,
                    pet_name: state.pet_name,
                }),
            });
            state = Edupets.applyServerSnapshot(username, response.user);
            if (statusNode) {
                statusNode.textContent = "Guardado";
            }
        } catch (error) {
            if (statusNode) {
                statusNode.textContent = error.message;
            }
        }
        render();
    }

    if (nameInput) {
        nameInput.addEventListener("input", () => {
            clearTimeout(nameTimer);
            nameTimer = setTimeout(saveName, 550);
        });
    }

    setInterval(() => {
        state.happiness = Edupets.clamp(state.happiness - 1);
        state.food = Edupets.clamp(state.food - 1);
        state.sleep = Edupets.clamp(state.sleep - 1);
        state.lastTick = Date.now();
        render();
    }, 60000);

    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") {
            syncNow(true);
        }
    });
    window.addEventListener("pagehide", () => syncNow(true));
    window.addEventListener("beforeunload", () => syncNow(true));

    render();
})();
