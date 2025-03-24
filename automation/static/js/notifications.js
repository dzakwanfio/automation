document.addEventListener("DOMContentLoaded", function () {
    let messagesContainer = document.getElementById("django-messages");

    if (messagesContainer) {
        let messages = messagesContainer.getElementsByTagName("span");

        for (let i = 0; i < messages.length; i++) {
            let messageText = messages[i].getAttribute("data-message");
            let messageType = messages[i].getAttribute("data-type");

            if (messageText) {
                alert((messageType === "success" ? "✅ Berhasil: " : "❌ Gagal: ") + messageText);
            }
        }
    }
});
