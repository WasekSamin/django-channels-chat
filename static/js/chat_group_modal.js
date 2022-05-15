window.addEventListener("DOMContentLoaded", () => {
    const chatGroupModal = document.getElementById("chat__groupModal");
    const addPeople = chatGroupModal.querySelector("#add__people");

    const finishGroup = document.getElementById("finish_create_group");
    const cancelGroup = document.getElementById("cancel_create_group");

    // Cancel group creation
    const makeGroupCreationCancel = () => {
        chatGroupModal.classList.remove("show__chatModal");
        addPeople.innerHTML = "";
    }

    // On cancel button click, cancel group creation
    cancelGroup.addEventListener("click", () => {
        makeGroupCreationCancel();
    })

    document.addEventListener("click", (e) => {
        if (e.target.closest("#chat__groupModal > div") || e.target.closest("#create__chatGroup") || e.target.closest("#create__chatGroupForMobile")) return;
        makeGroupCreationCancel();
    })
})