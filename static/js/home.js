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
            }
        }
    }
})