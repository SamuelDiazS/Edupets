(function () {
    const root = document.getElementById("shop-app");
    if (!root || !window.Edupets) {
        return;
    }

    const username = root.dataset.username;
    const serverState = Edupets.readJsonScript("shop-data");
    let state = Edupets.mergeServerState(username, serverState);
    state = Edupets.applyElapsedDecay(state);
    Edupets.saveState(username, state);

    const coinsNode = root.querySelector('[data-role="coins"]');
    const messageNode = document.getElementById("shop-message");

    function render() {
        if (coinsNode) {
            coinsNode.textContent = state.coins;
        }
        root.querySelectorAll(".shop-item").forEach((item) => {
            const price = Number.parseInt(item.dataset.price || "0", 10);
            const button = item.querySelector(".buy-button");
            if (button) {
                button.disabled = state.coins < price;
            }
        });
    }

    async function buy(itemId) {
        const button = root.querySelector(`.buy-button[data-item-id="${itemId}"]`);
        if (button) {
            button.disabled = true;
        }
        if (messageNode) {
            messageNode.textContent = "";
        }
        try {
            const payload = await Edupets.api("/api/shop/buy", {
                method: "POST",
                body: JSON.stringify({
                    csrf_token: Edupets.csrfToken,
                    item_id: itemId,
                }),
            });
            state = Edupets.applyServerSnapshot(username, payload.user);
            if (messageNode) {
                messageNode.textContent = `${payload.item.name} comprado`;
            }
        } catch (error) {
            if (messageNode) {
                messageNode.textContent = error.message;
            }
        }
        render();
    }

    root.querySelectorAll(".buy-button").forEach((button) => {
        button.addEventListener("click", () => buy(button.dataset.itemId));
    });

    render();
})();
