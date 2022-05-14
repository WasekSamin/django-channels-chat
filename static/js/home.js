window.addEventListener("DOMContentLoaded", () => {
    const createChatGroup = document.getElementById("create__chatGroup");
    const chatLeftBottomUsers = document.getElementById("chat__leftBottomUsers");
    const finishCreateGroupBtn = document.getElementById("finish_create_group");
    const chatGroupModalErrorMsg = document.getElementById("group__modalErrorMsg");
    let groupSelectedUsers = [];

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
            } else if (data.group_created) {
                
            } else if (!data.group_created) {
                alert("Group create failed! Please try again...");
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
                const userTagsInfo = user.querySelector("p");

                const userId = Number(userTagsInfo.id.split("-")[1]);
                const image = document.getElementById(`account-${userId}`).querySelector("img").src;
                const username = userTagsInfo.innerText || userTagsInfo.textContent;

                userInfo.push({id: userId, username: username, image: image});
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
        console.log(groupUsers);

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