window.addEventListener("DOMContentLoaded", () => {
    let conn = false;

    const ws = new WebSocket("ws://127.0.0.1:8000/ws/chat/");

    ws.addEventListener("open", () => {
        console.log("Opened");
        conn = true;

        ws.send(JSON.stringify({
            command: "join",
            groupName: "public"
        }));
    });

    ws.onmessage = e => {
        if (conn) {
            const data = JSON.parse(e.data);
            console.log(data);

            // Updating user online status
            if (data.connect) {
                const account = document.getElementById(`account-${data.user_id}`);

                if (account) {
                    const accountStatus = account.querySelector(".user__status").querySelector(".iconify");
                    
                    accountStatus.classList.remove("text-rose-500");
                    accountStatus.classList.add("text-green-500");
                }
            } else if (data.disconnect) {
                const account = document.getElementById(`account-${data.user_id}`);

                if (account) {
                    const accountStatus = account.querySelector(".user__status").querySelector(".iconify");
                    
                    accountStatus.classList.remove("text-green-500");
                    accountStatus.classList.add("text-rose-500");
                }
            } else if (data.create_message_success) {
                ws.send(JSON.stringify({
                    ...data,
                    receiverCurrentLoc: "home",
                    command: "receive_message"
                }));
            } else if (data.receive_message_success) {
                if (data.show_as_notification) {
                    // Updating last message on receiver side
                    const account = document.getElementById(`account-${data.sender_id}`);
                    const lastMsg = account.querySelector(".last_message");
                    lastMsg.innerText = data.message;

                    const status = document.getElementById(`status-${data.sender_id}`);
                    const showStatus = status.querySelector(".iconify");

                    showStatus.classList.remove("text-transparent");
                    showStatus.classList.add("text-indigo-400");
                }
            }
        }
    }
})