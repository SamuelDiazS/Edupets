(function () {
    const themeToggle = document.querySelector(".theme-toggle");
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfMeta ? csrfMeta.content : "";

    function setTheme(theme) {
        const isDark = theme === "dark";
        document.documentElement.dataset.theme = isDark ? "dark" : "light";
        if (themeToggle) {
            themeToggle.setAttribute("aria-pressed", String(isDark));
            themeToggle.setAttribute("aria-label", isDark ? "Activar modo claro" : "Activar modo oscuro");
            themeToggle.querySelector("span").textContent = isDark ? "☀" : "☾";
        }
    }

    if (themeToggle) {
        setTheme(document.documentElement.dataset.theme || "light");
        themeToggle.addEventListener("click", () => {
            const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
            setTheme(nextTheme);
            try {
                localStorage.setItem("edupets_theme", nextTheme);
            } catch {
            }
        });
    }

    function clamp(value, min = 0, max = 100) {
        const number = Number.parseInt(value, 10);
        if (Number.isNaN(number)) {
            return min;
        }
        return Math.max(min, Math.min(max, number));
    }

    function readJsonScript(id) {
        const node = document.getElementById(id);
        if (!node) {
            return {};
        }
        try {
            return JSON.parse(node.textContent || "{}");
        } catch {
            return {};
        }
    }

    function stateKey(username) {
        return `edupets_state_${username}`;
    }

    function normalizeState(raw) {
        const state = raw && typeof raw === "object" ? raw : {};
        return {
            username: String(state.username || ""),
            coins: Math.max(0, Number.parseInt(state.coins || 0, 10)),
            happiness: clamp(state.happiness ?? 100),
            food: clamp(state.food ?? 100),
            sleep: clamp(state.sleep ?? 100),
            pet_name: String(state.pet_name || "Mi Mascota").slice(0, 30),
            progress: state.progress && typeof state.progress === "object" ? state.progress : {},
            tasks: state.tasks && typeof state.tasks === "object" ? state.tasks : {},
            lastTick: Number.parseInt(state.lastTick || Date.now(), 10),
        };
    }

    function loadState(username) {
        try {
            const stored = localStorage.getItem(stateKey(username));
            return stored ? normalizeState(JSON.parse(stored)) : null;
        } catch {
            return null;
        }
    }

    function saveState(username, state) {
        const normalized = normalizeState(state);
        localStorage.setItem(stateKey(username), JSON.stringify(normalized));
        updateLogoutFields(username, normalized);
        return normalized;
    }

    function mergeServerState(username, serverState, options = {}) {
        const preferLocalStats = options.preferLocalStats !== false;
        const server = normalizeState(serverState);
        const local = loadState(username);
        let merged = server;

        if (local && preferLocalStats) {
            merged = {
                ...server,
                happiness: local.happiness,
                food: local.food,
                sleep: local.sleep,
                pet_name: local.pet_name || server.pet_name,
                lastTick: local.lastTick || Date.now(),
            };
        }

        if (!merged.lastTick) {
            merged.lastTick = Date.now();
        }
        return saveState(username, merged);
    }

    function applyServerSnapshot(username, snapshot) {
        const local = loadState(username);
        const merged = normalizeState({
            ...(local || {}),
            ...(snapshot || {}),
            lastTick: local ? local.lastTick : Date.now(),
        });
        return saveState(username, merged);
    }

    function applyElapsedDecay(state) {
        const next = normalizeState(state);
        const now = Date.now();
        const lastTick = Number.isFinite(next.lastTick) ? next.lastTick : now;
        const elapsedMinutes = Math.floor((now - lastTick) / 60000);

        if (elapsedMinutes > 0) {
            next.happiness = clamp(next.happiness - elapsedMinutes);
            next.food = clamp(next.food - elapsedMinutes);
            next.sleep = clamp(next.sleep - elapsedMinutes);
            next.lastTick = lastTick + elapsedMinutes * 60000;
        } else {
            next.lastTick = lastTick;
        }
        return next;
    }

    async function api(url, options = {}) {
        const headers = new Headers(options.headers || {});
        headers.set("Content-Type", "application/json");
        headers.set("X-CSRF-Token", csrfToken);

        const response = await fetch(url, {
            credentials: "same-origin",
            ...options,
            headers,
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(payload.detail || "No se pudo completar la acción.");
        }
        return payload;
    }

    function updateLogoutFields(username, state) {
        const current = state || loadState(username);
        if (!current) {
            return;
        }
        document.querySelectorAll("[data-logout-field]").forEach((field) => {
            const key = field.dataset.logoutField;
            if (key in current) {
                field.value = current[key];
            }
        });
    }

    document.addEventListener("submit", (event) => {
        const form = event.target.closest(".logout-form");
        const appRoot = document.querySelector("[data-username]");
        if (form && appRoot) {
            updateLogoutFields(appRoot.dataset.username);
        }
    });

    window.Edupets = {
        csrfToken,
        clamp,
        readJsonScript,
        loadState,
        saveState,
        mergeServerState,
        applyServerSnapshot,
        applyElapsedDecay,
        api,
        updateLogoutFields,
    };
})();
