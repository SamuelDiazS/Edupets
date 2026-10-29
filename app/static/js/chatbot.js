(function () {
    const root = document.querySelector("[data-math-chat]");
    if (!root || !window.Edupets) {
        return;
    }

    const panel = root.querySelector("[data-chat-panel]");
    const openButton = root.querySelector("[data-chat-open]");
    const closeButton = root.querySelector("[data-chat-close]");
    const form = root.querySelector("[data-chat-form]");
    const input = root.querySelector("#math-chat-input");
    const sendButton = root.querySelector(".math-chat-send");
    const messagesNode = root.querySelector("[data-chat-messages]");
    const statusNode = root.querySelector("[data-chat-status]");
    const mathHistory = [];
    let requestInFlight = false;

    function setOpen(isOpen) {
        panel.hidden = !isOpen;
        openButton.setAttribute("aria-expanded", String(isOpen));
        if (isOpen) {
            input.focus();
        } else {
            openButton.focus();
        }
    }

    function appendMessage(text, role) {
        const message = document.createElement("p");
        message.className = `math-chat-bubble is-${role}`;
        message.textContent = text;
        messagesNode.appendChild(message);
        messagesNode.scrollTop = messagesNode.scrollHeight;
        return message;
    }

    function setBusy(isBusy) {
        requestInFlight = isBusy;
        input.disabled = isBusy;
        sendButton.disabled = isBusy;
        form.setAttribute("aria-busy", String(isBusy));
        statusNode.textContent = isBusy ? "El tutor está pensando…" : "";
        if (isBusy) {
            const indicator = document.createElement("p");
            indicator.className = "math-chat-bubble is-assistant is-typing";
            indicator.textContent = "Preparando una respuesta…";
            indicator.dataset.typing = "true";
            messagesNode.appendChild(indicator);
            messagesNode.scrollTop = messagesNode.scrollHeight;
        } else {
            messagesNode.querySelector("[data-typing]")?.remove();
        }
    }

    openButton.addEventListener("click", () => setOpen(panel.hidden));
    closeButton.addEventListener("click", () => setOpen(false));

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = input.value.trim();
        if (!message || requestInFlight) {
            return;
        }
        if (message.length > 500) {
            statusNode.textContent = "Escribe un mensaje de hasta 500 caracteres.";
            return;
        }

        appendMessage(message, "user");
        input.value = "";
        setBusy(true);
        try {
            const payload = await Edupets.api("/api/chat", {
                method: "POST",
                body: JSON.stringify({ message, history: mathHistory.slice(-4) }),
            });
            appendMessage(payload.reply, "assistant");
            if (payload.math_allowed) {
                mathHistory.push(message);
            }
        } catch (error) {
            appendMessage(error.message || "No se pudo enviar el mensaje. Inténtalo más tarde.", "assistant");
        } finally {
            setBusy(false);
            input.focus();
        }
    });
})();