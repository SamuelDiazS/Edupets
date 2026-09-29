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
            const itemId = item.dataset.item;
            const inventoryCount = root.querySelector(`[data-inventory-count="${itemId}"]`);
            const ownedQuantity = (state.inventory || []).find((entry) => entry.item_id === itemId)?.quantity || 0;
            if (inventoryCount) {
                inventoryCount.textContent = `Inventario ×${ownedQuantity}`;
            }
            if (button) {
                const petId = item.dataset.petId;
                if (petId) {
                    const isCurrent = state.pet_type === petId;
                    const isOwned = (state.owned_pets || []).includes(petId);
                    item.classList.toggle("is-current-pet", isCurrent);
                    button.textContent = isCurrent ? "Mascota actual" : isOwned ? "Usar" : "Comprar";
                    button.disabled = isCurrent || (!isOwned && state.coins < price);
                } else {
                    button.disabled = state.coins < price;
                }
            }
        });
    }

    async function buy(itemId) {
        const button = root.querySelector(`.buy-button[data-item-id="${itemId}"], .buy-button[data-pet-id="${itemId}"]`);
        const petId = button?.dataset.petId;
        if (button) {
            button.disabled = true;
        }
        if (messageNode) {
            messageNode.textContent = "";
        }
        try {
            const payload = await Edupets.api(petId ? "/api/shop/pet" : "/api/shop/buy", {
                method: "POST",
                body: JSON.stringify({
                    csrf_token: Edupets.csrfToken,
                    ...(petId ? { pet_id: petId } : { item_id: itemId }),
                }),
            });
            state = Edupets.applyServerSnapshot(username, payload.user);
            if (messageNode) {
                messageNode.textContent = petId
                    ? `${payload.item.name} ${payload.purchased ? "comprado y seleccionado" : "seleccionado"}`
                    : `${payload.item.name} comprado`;
            }
        } catch (error) {
            if (messageNode) {
                messageNode.textContent = error.message;
            }
        }
        render();
    }

    root.querySelectorAll(".buy-button").forEach((button) => {
        button.addEventListener("click", () => buy(button.dataset.itemId || button.dataset.petId));
    });

    render();
})();
