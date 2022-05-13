window.addEventListener("DOMContentLoaded", () => {
    const chatRightMiddle = document.getElementById("chat__rightMiddle");
    const chatMsgInput = document.getElementById("chat__messageInput");
    const chatSubmitBtn = document.getElementById("chat__submitBtn");
    const chatMsgForm = document.getElementById("chat__msgForm");

    const ws = new WebSocket("ws://127.0.0.1:8000/ws/chat/");
    let conn = false;

    ws.addEventListener("open", () => {
        conn = true;
        console.log("OPENED");

        const currentLoc = window.location.href;
        ws.send(JSON.stringify({
            command: "join",
            privateChat: true,
            groupName: currentLoc
        }));

        // By default, submit button is disabled
        chatSubmitBtn.disabled = true;
        chatRightMiddle.scroll({top: chatRightMiddle.scrollHeight});

        // If user type something, enable the submit button, else disable it
        chatMsgInput.addEventListener("keyup", e => {
            const msgVal = e.target.value;

            if (msgVal.trim() === "") {
                chatSubmitBtn.disabled = true;
                chatSubmitBtn.querySelector(".iconify").classList.remove("text-slate-300");
                chatSubmitBtn.querySelector(".iconify").classList.add("text-slate-500");
            } else {
                chatSubmitBtn.disabled = false;
                chatSubmitBtn.querySelector(".iconify").classList.remove("text-slate-500");
                chatSubmitBtn.querySelector(".iconify").classList.add("text-slate-300");
            }
        });

        chatMsgForm.addEventListener("submit", e => {
            e.preventDefault();

            if (chatMsgInput.value.trim() === "") return;
            
            sendMessage(chatMsgInput.value.trim());
        });

        // Send message via socket
        function sendMessage(msg) {
            ws.send(JSON.stringify({
                command: "send",
                message: msg,
                room: window.location.href
            }))
        }
    })

    ws.onmessage = e => {
        if (conn) {
            const data = JSON.parse(e.data);
            console.log("DATA:", data);

            // Updating user online status
            if (data.connect) {
                const account = document.getElementById(`account-${data.user_id}`);

                if (account) {
                    const accountStatus = account.querySelector(".user__status").querySelector(".iconify");
                    
                    accountStatus.classList.remove("text-rose-500");
                    accountStatus.classList.add("text-green-500");

                    const onlineStatus = document.getElementById("online__status");
                    onlineStatus.classList.remove("text-rose-500");
                    onlineStatus.classList.add("text-green-500");
                }
            } else if (data.disconnect) {
                const account = document.getElementById(`account-${data.user_id}`);

                if (account) {
                    const accountStatus = account.querySelector(".user__status").querySelector(".iconify");
                    
                    accountStatus.classList.remove("text-green-500");
                    accountStatus.classList.add("text-rose-500");

                    const onlineStatus = document.getElementById("online__status");
                    onlineStatus.classList.add("text-rose-500");
                    onlineStatus.classList.remove("text-green-500");
                }
            } else if (data.create_message_success) {   // Sender side
                ws.send(JSON.stringify({
                    ...data,
                    receiverCurrentLoc: "chatroom",
                    currentLoc: window.location.href,
                    command: "receive_message"
                }));
                
                let currentLoc = window.location.href.split("/");
                currentLoc = currentLoc[currentLoc.length - 2];
                const userId = document.getElementById("user__id");
                
                let senderId;

                if (userId) {
                    senderId = Number(userId.value);
                } else {
                    window.location.reload();
                }

                // Appending message on sender side
                if (currentLoc == data.room && data.sender_id === senderId) {
                    // Updating last message on sender side
                    const account = document.getElementById(`account-${data.receiver_id}`);
                    const lastMsg = account.querySelector(".last_message");

                    lastMsg.innerText = data.message;

                    const chatDiv = document.getElementById("chat__rightChatDiv");

                    const msgDiv = document.createElement("div");
                    msgDiv.setAttribute("class", "flex gap-x-1 w-1/2 place-self-end")
                    msgDiv.innerHTML = `
                        <div>
                            <img src="/static/images/user.png" class="w-[20px] min-w-[20px] h-[20px] mt-1 object-contain" alt="">
                        </div>
                        <div class="flex flex-col gap-y-1 text-slate-300 text-sm">
                            <h5 class="font-semibold chat__rightMiddleUsername">${data.sender_username}</h5>
                            <p class="">${data.message}</p>
                            <p class="text-xs">${data.created_at}</p>
                        </div>
                    `
                    chatDiv.appendChild(msgDiv);

                    chatRightMiddle.scroll({top: chatRightMiddle.scrollHeight, behavior: "smooth"});
                }
            } else if (data.receive_message_success) {  // Receiver side
                let currentLoc = window.location.href.split("/");
                currentLoc = currentLoc[currentLoc.length - 2];

                if (currentLoc === data.room) {
                    // Append message on receiver side
                    if (data.append_to_message_field) {
                        const account = document.getElementById(`account-${data.sender_id}`);
                        // Updating last message on sender side
                        const lastMsg = account.querySelector(".last_message");

                        lastMsg.innerText = data.message;

                        const chatDiv = document.getElementById("chat__rightChatDiv");

                        const msgDiv = document.createElement("div");
                        msgDiv.setAttribute("class", "flex gap-x-1 w-1/2")
                        msgDiv.innerHTML = `
                            <div>
                                <img src="/static/images/user.png" class="w-[20px] min-w-[20px] h-[20px] mt-1 object-contain" alt="">
                            </div>
                            <div class="flex flex-col gap-y-1 text-slate-300 text-sm">
                                <h5 class="font-semibold chat__rightMiddleUsername">${data.sender_username}</h5>
                                <p class="">${data.message}</p>
                                <p class="text-xs">${data.created_at}</p>
                            </div>
                        `
                        chatDiv.appendChild(msgDiv);

                        chatRightMiddle.scroll({top: chatRightMiddle.scrollHeight, behavior: "smooth"});
                    }
                } else {    // Receiver side
                    // If current user is in different chatroom
                    const account = document.getElementById(`account-${data.sender_id}`);
                    // Updating last message on sender side
                    const lastMsg = account.querySelector(".last_message");

                    lastMsg.innerText = data.message;

                    const chatDiv = document.getElementById("chat__rightChatDiv");

                    const status = document.getElementById(`status-${data.sender_id}`);
                    const showStatus = status.querySelector(".iconify")

                    showStatus.classList.remove("text-transparent");
                    showStatus.classList.add("text-indigo-400");
                }
            }
        }
    }
})