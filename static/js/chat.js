window.addEventListener("DOMContentLoaded", () => {
    const chatRightMiddle = document.getElementById("chat__rightMiddle");
    const chatMsgInput = document.getElementById("chat__messageInput");
    const chatSubmitBtn = document.getElementById("chat__submitBtn");
    const chatMsgForm = document.getElementById("chat__msgForm");

    const createChatGroup = document.getElementById("create__chatGroup");
    const chatLeftBottomUsers = document.getElementById("chat__leftBottomUsers");

    const finishCreateGroupBtn = document.getElementById("finish_create_group");
    const chatGroupModalErrorMsg = document.getElementById("group__modalErrorMsg");
    let groupSelectedUsers = [];

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
            chatMsgForm.reset();
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
                    senderId = JSON.parse(userId.innerText);
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
                            <p class="break-all">${data.message}</p>
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
                        // Updating last message on receiver side
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
                                <p class="break-all">${data.message}</p>
                                <p class="text-xs">${data.created_at}</p>
                            </div>
                        `
                        chatDiv.appendChild(msgDiv);

                        chatRightMiddle.scroll({top: chatRightMiddle.scrollHeight, behavior: "smooth"});
                    }
                } else {    // Receiver side
                    // If current user is in different chatroom
                    const account = document.getElementById(`account-${data.sender_id}`);
                    // Updating last message on receiver side
                    const lastMsg = account.querySelector(".last_message");

                    lastMsg.innerText = data.message;

                    const chatDiv = document.getElementById("chat__rightChatDiv");

                    const status = document.getElementById(`status-${data.sender_id}`);
                    const showStatus = status.querySelector(".iconify")

                    showStatus.classList.remove("text-transparent");
                    showStatus.classList.add("text-indigo-400");
                }
            } else if (data.group_created) {
                const a = document.createElement("a");
                const userId = JSON.parse(document.getElementById("user__id").innerText);

                const foundUser = data.users.find(user => user === userId);

                if (foundUser) {
                    a.setAttribute("href", `/group/${data.room}/`);
                    a.setAttribute("class", "flex items-center");
                    a.setAttribute("id", `group-${data.group_id}`);

                    a.innerHTML = `
                        <span class="iconify text-lg mr-1 text-sky-300" data-icon="el:group-alt"></span>
                        <div class="flex flex-col gap-y-0.5 pl-0.5 chat__userInfo">
                            <p id="group-${data.group_id}" class="font-semibold text-slate-300 tracking-wide whitespace-nowrap overflow-hidden text-ellipsis">${data.given_room_name}</p>
                            <p class="text-slate-300 text-xs whitespace-nowrap overflow-hidden text-ellipsis last_message">There is no message yet!</p>
                            <p class="flex items-center text-xs font-medium text-slate-400 user__status">Status: <span class="iconify text-xl text-green-500" data-icon="ci:dot-03-m"></span></p>
                        </div>
                        <div id="status-${data.group_id}">
                            <span class="iconify text-xl text-transparent" data-icon="ci:dot-03-m"></span>
                        </div>
                    `

                    chatLeftBottomUsers.appendChild(a);

                    if (data.creator === userId) {
                        window.location.href = `/group/${data.room}`;
                    }
                }
            } else if (data.group_create_message_success) {
                ws.send(JSON.stringify({
                    ...data,
                    receiverCurrentLoc: "privateChatroom",
                    command: "group_receive_message"
                }));
            } else if (data.group_receive_message_success) {
                console.log("FROM GROUP RECEIVE MESSAGE:", data);
                if (data.show_as_notification) {
                    // Updating last message on receiver side
                    const group = document.getElementById(`group-${data.group_id}`);
                    
                    if(group) {
                        const lastMsg = group.querySelector(".last_message");
                        lastMsg.innerText = data.message;

                        const status = document.getElementById(`group-status-${data.group_id}`);
                        const showStatus = status.querySelector(".iconify");

                        showStatus.classList.remove("text-transparent");
                        showStatus.classList.add("text-indigo-400");
                    }
                }
            }
        }
    }

    // If Create group button is clicked
    createChatGroup.addEventListener("click", () => {
        // Getting all the users
        const users = chatLeftBottomUsers.querySelectorAll(".chat__userInfo");
        const chatGroupModal = document.getElementById("chat__groupModal");
        const addPeople = chatGroupModal.querySelector("#add__people");

        addPeople.innerHTML = `
            <div id="chat__groupSpinner" class="flex items-center justify-center">
                <span class="iconify text-3xl text-slate-200" data-icon="icomoon-free:spinner2"></span>
            </div>
        `

        // Appending user id and name into userInfo array
        const promiseUserInfo =  new Promise((resolve, reject) => {
            let userInfo = [];

            users.forEach(user => {
                const userTagsInfo = user.querySelector(".chat__userUsername");

                if (userTagsInfo) {
                    const userId = Number(userTagsInfo.id.split("-")[1]);
                    const image = document.getElementById(`account-${userId}`).querySelector("img").src;
                    const username = userTagsInfo.innerText || userTagsInfo.textContent;

                    userInfo.push({id: userId, username: username, image: image});
                }
            })

            if (userInfo.length > 0)
                resolve(userInfo);
            else
                reject("Something is wrong!");
        })

        promiseUserInfo.then(users => {
            chatGroupModal.classList.add("show__chatModal");
            
            setTimeout(() => {
                addPeople.innerHTML = "";

                users.map(user => {
                    const userDiv = document.createElement("div");
    
                    userDiv.setAttribute("user-", user.id);
                    userDiv.setAttribute("class", "flex items-center justify-between pr-3");
    
                    userDiv.innerHTML = `
                        <label for="selected-user-${user.id}" class="flex w-full items-center gap-x-1 cursor-pointer">
                            <img src="${user.image}" class="w-[20px] min-w-[20px] h-[20px] object-contain" alt="">
                            <p class="text-slate-200 font-medium chat__groupUsername mr-1">${user.username}</p>
                        </label>
                        <input id="selected-user-${user.id}" type="checkbox" class="indeterminate:bg-gray-300 default:ring-2 cursor-pointer selected_user_for_chatGroup" />
                    `
    
                    addPeople.appendChild(userDiv);
                });

                const selectedUserLabels = document.querySelectorAll(".selected_user_for_chatGroup");
                // console.log(selectedUserLabels);
                
                selectedUserLabels.forEach(label => {
                    label.addEventListener("click", (e) => {
                        if (e.target.checked) {
                            const userId = Number(e.target.id.split("-")[2]);
                            groupSelectedUsers.push(userId);
                        } else if (!e.target.checked) {
                            const userId = Number(e.target.id.split("-")[2]);
                            const foundUserIdx = groupSelectedUsers.findIndex(user => user === userId);
                            groupSelectedUsers.splice(foundUserIdx, 1);
                        }
                    })
                });
            }, 500);
        }).catch(err => {
            console.error(err);
        })
    })

    finishCreateGroupBtn.addEventListener("click", () => {
        chatGroupModalErrorMsg.classList.add("hidden");

        const groupName = document.getElementById("group_name");

        if (!groupName || groupName.value.trim() === "") {
            chatGroupModalErrorMsg.innerText = "Please enter your room name!";
            chatGroupModalErrorMsg.classList.remove("hidden");
        } else if (groupSelectedUsers.length === 0) {
            chatGroupModalErrorMsg.innerText = "Please select atleast one user!";
            chatGroupModalErrorMsg.classList.remove("hidden");
        } else {
            chatGroupModalErrorMsg.classList.add("hidden");
            const addPeople = document.getElementById("add__people");

            document.getElementById("chat__groupOptions").style.display = "none";
            addPeople.innerHTML = `
                <div id="chat__groupSpinner" class="flex items-center justify-center">
                    <span class="iconify text-3xl text-slate-200" data-icon="icomoon-free:spinner2"></span>
                </div>
            `

            createGroup(groupName.value.trim(), groupSelectedUsers);

            // Clearing group modal field
            groupName.value = "";
            groupSelectedUsers = [];
        }
    });

    // Creating group using socket
    function createGroup(roomName, groupUsers) {
        const userId = document.getElementById("user__id");

        let senderId;

        if (userId) {
            senderId = JSON.parse(userId.innerText);
        } else {
            window.location.reload();
        }

        const foundSenderId = groupUsers.find(user => user === senderId);

        if (!foundSenderId) {
            groupUsers.push(senderId);
        }

        ws.send(JSON.stringify({
            command: "join",
            groupCreate: true,
            roomName: roomName,
            creatorId: senderId,
            users: groupUsers
        }));
    }
})