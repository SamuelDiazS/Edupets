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
    const inventoryList = document.getElementById("inventory-items");
    const dropTarget = document.getElementById("pet-drop-target");
    const feedbackNode = document.getElementById("pet-feedback");
    let nameTimer = null;
    let syncInFlight = null;
    let lastBeaconAt = 0;
    let activePointer = null;
    let useInFlight = false;

    const inventoryImages = {
        pollo: "pescado.png",
        juguete: "juguete.png",
        caramelos: "caramelos.png",
    };

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

    function renderInventory() {
        if (!inventoryList) {
            return;
        }
        inventoryList.innerHTML = "";
        const entries = state.inventory || [];
        if (!entries.length) {
            const empty = document.createElement("p");
            empty.className = "inventory-empty";
            empty.textContent = "Todavía no tienes objetos.";
            inventoryList.appendChild(empty);
            return;
        }

        entries.forEach((entry) => {
            const card = document.createElement("article");
            card.className = "inventory-item";
            card.dataset.itemId = entry.item_id;
            card.dataset.inventoryItem = "";
            card.setAttribute("aria-label", `${entry.name}, cantidad ${entry.quantity}`);

            const image = document.createElement("img");
            image.src = `/static/images/${inventoryImages[entry.item_id] || ""}`;
            image.alt = "";
            const name = document.createElement("span");
            name.className = "inventory-item-name";
            name.textContent = entry.name;
            const quantity = document.createElement("strong");
            quantity.className = "inventory-item-quantity";
            quantity.textContent = `×${entry.quantity}`;
            const useButton = document.createElement("button");
            useButton.className = "secondary-button inventory-use-button";
            useButton.type = "button";
            useButton.dataset.useItem = entry.item_id;
            useButton.textContent = "Usar";
            card.append(image, name, quantity, useButton);
            inventoryList.appendChild(card);
        });
    }

    function render() {
        renderStats();
        renderTasks();
        renderInventory();
        Edupets.saveState(username, state);
    }

    async function useItem(itemId) {
        if (useInFlight) {
            return;
        }
        useInFlight = true;
        root.setAttribute("aria-busy", "true");
        root.querySelectorAll("[data-use-item]").forEach((button) => {
            button.disabled = true;
        });
        if (feedbackNode) {
            feedbackNode.textContent = "";
            feedbackNode.classList.remove("is-error");
        }
        try {
            const response = await Edupets.api("/api/pet/use-item", {
                method: "POST",
                body: JSON.stringify({ csrf_token: Edupets.csrfToken, item_id: itemId }),
            });
            state = Edupets.applyServerSnapshot(username, response.user);
            if (feedbackNode) {
                const item = (state.inventory || []).find((entry) => entry.item_id === itemId);
                feedbackNode.textContent = item ? "Objeto usado." : "Objeto usado. Ya no quedan unidades.";
            }
        } catch (error) {
            if (feedbackNode) {
                feedbackNode.textContent = error.message;
                feedbackNode.classList.add("is-error");
            }
        } finally {
            useInFlight = false;
            root.removeAttribute("aria-busy");
            render();
        }
    }

    function clearDrag() {
        if (!activePointer) {
            return;
        }
        activePointer.card.classList.remove("is-dragging");
        activePointer.ghost?.remove();
        dropTarget?.classList.remove("is-drop-target");
        activePointer = null;
    }

    root.addEventListener("pointerdown", (event) => {
        const card = event.target.closest("[data-inventory-item]");
        if (!card || event.target.closest("button") || useInFlight || event.button !== 0) {
            return;
        }
        activePointer = {
            card,
            itemId: card.dataset.itemId,
            pointerId: event.pointerId,
            startX: event.clientX,
            startY: event.clientY,
            ghost: null,
            dragging: false,
        };
        card.setPointerCapture(event.pointerId);
    });

    root.addEventListener("pointermove", (event) => {
        if (!activePointer || activePointer.pointerId !== event.pointerId) {
            return;
        }
        const distance = Math.hypot(event.clientX - activePointer.startX, event.clientY - activePointer.startY);
        if (!activePointer.dragging && distance < 8) {
            return;
        }
        if (!activePointer.dragging) {
            activePointer.dragging = true;
            activePointer.card.classList.add("is-dragging");
            activePointer.ghost = activePointer.card.cloneNode(true);
            activePointer.ghost.classList.add("inventory-drag-ghost");
            document.body.appendChild(activePointer.ghost);
        }
        activePointer.ghost.style.left = `${event.clientX}px`;
        activePointer.ghost.style.top = `${event.clientY}px`;
        const overPet = document.elementFromPoint(event.clientX, event.clientY)?.closest("#pet-drop-target");
        dropTarget?.classList.toggle("is-drop-target", Boolean(overPet));
    });

    root.addEventListener("pointerup", (event) => {
        if (!activePointer || activePointer.pointerId !== event.pointerId) {
            return;
        }
        const itemId = activePointer.itemId;
        const wasDragging = activePointer.dragging;
        const droppedOnPet = wasDragging && Boolean(
            document.elementFromPoint(event.clientX, event.clientY)?.closest("#pet-drop-target"),
        );
        clearDrag();
        if (droppedOnPet) {
            useItem(itemId);
        }
    });

    root.addEventListener("pointercancel", clearDrag);
    root.addEventListener("click", (event) => {
        const button = event.target.closest("[data-use-item]");
        if (button) {
            useItem(button.dataset.useItem);
        }
    });

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
