window.addEventListener("DOMContentLoaded", () => {
    const username = document.getElementById("username");
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    const confPassword = document.getElementById("conf_password");
    const regForm = document.getElementById("register__form");
    const errorMsg = document.getElementById("error__msg");
    const registerSubmitBtn = document.getElementById("register__submitButton");
    const registerBtnSpinner = document.getElementById("register__buttonLoader");

    // Email validation
    const validateEmail = (email) => {
        var re =
        /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    };

    const getCookie = (name) => {
        var cookieValue = null;
        if (document.cookie && document.cookie != "") {
          var cookies = document.cookie.split(";");
          for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == name + "=") {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
    };

    regForm.addEventListener("submit", e => {
        e.preventDefault();

        errorMsg.classList.add("hidden");

        if (!username.value || username.value.trim() === "") {
            errorMsg.innerText = "Username field is required!";
            errorMsg.classList.remove("hidden");
            errorMsg.scrollIntoView({behavior: "smooth"});
        } else if (!email.value || email.value.trim() === "") {
            errorMsg.innerText = "Email field is required!";
            errorMsg.classList.remove("hidden");
            errorMsg.scrollIntoView({behavior: "smooth"});
        } else if (!password.value || password.value.trim() === "") {
            errorMsg.innerText = "Password field is required!";
            errorMsg.classList.remove("hidden");
            errorMsg.scrollIntoView({behavior: "smooth"});
        } else if (!confPassword.value || confPassword.value.trim() === "") {
            errorMsg.innerText = "Confirm password field is required!";
            errorMsg.classList.remove("hidden");
            errorMsg.scrollIntoView({behavior: "smooth"});
        } else {
            const emailValidation = validateEmail(email.value.normalize());

            if (emailValidation) {
                if (password.value.trim().length > 5) {
                    if (password.value.normalize() === confPassword.value.normalize()) {
                        u = username.value.normalize();
                        e = email.value.normalize();
                        p = password.value.normalize();

                        // Submit button effect
                        registerSubmitBtn.classList.remove("bg-indigo-500");
                        registerSubmitBtn.classList.remove("ripple__button");
                        registerSubmitBtn.classList.add("bg-slate-700");
                        registerSubmitBtn.disabled = true;
                        registerBtnSpinner.classList.remove("hidden");

                        createAccount(u, e, p);
                    } else {
                        errorMsg.innerText = "Two password fields did not match!";
                        errorMsg.classList.remove("hidden");
                        errorMsg.scrollIntoView({behavior: "smooth"});
                    }
                } else {
                    errorMsg.innerText = "Password is too short!";
                    errorMsg.classList.remove("hidden");
                    errorMsg.scrollIntoView({behavior: "smooth"});
                }
            } else {
                errorMsg.innerText = "Please enter a valid email address!";
                errorMsg.classList.remove("hidden");
                errorMsg.scrollIntoView({behavior: "smooth"});
            }
        }
    })

    async function createAccount(username, email, password) {
        const CSRFTOKEN = getCookie("csrftoken");

        let formData = new FormData();
        formData.append("username", username);
        formData.append("email", email);
        formData.append("password", password);

        await fetch("/account/create-account/", {
            method: "POST",
            headers: {
                "X-CSRFToken": CSRFTOKEN
            },
            body: formData
        }).then(res => {
            if (res.ok) {
                return res.json();
            } else {
                alert("Something is wrong! Please try again...");
            }
        }).then(data => {
            if (data.error) {
                alert("Something is wrong! Please try again...");
            } else if (!data.error && data.user_exist) {
                errorMsg.innerText = "Email is already in use!";
                errorMsg.classList.remove("hidden");
                errorMsg.scrollIntoView({behavior: "smooth"});
            } else if (!data.error && data.user_created) {
                window.location.href = "/";
            }
        }).catch(err => console.error(err));

        // Submit button effect
        registerSubmitBtn.classList.add("bg-indigo-500");
        registerSubmitBtn.classList.add("ripple__button");
        registerSubmitBtn.classList.remove("bg-slate-700");
        registerSubmitBtn.disabled = false;
        registerBtnSpinner.classList.add("hidden");
    }
})