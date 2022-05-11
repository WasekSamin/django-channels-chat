window.addEventListener("DOMContentLoaded", () => {
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    const loginForm = document.getElementById("login__form");
    const errorMsg = document.getElementById("error__msg");
    const loginSubmitBtn = document.getElementById("login__submitButton");
    const loginBtnSpinner = document.getElementById("login__buttonLoader");

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

    loginForm.addEventListener("submit", e => {
        e.preventDefault();

        errorMsg.classList.add("hidden");

        if (!email.value || email.value.trim() === "") {
            errorMsg.innerText = "Email field is required!";
            errorMsg.classList.remove("hidden");
            errorMsg.scrollIntoView({behavior: "smooth"});
        } else if (!password.value || password.value.trim() === "") {
            errorMsg.innerText = "Password field is required!";
            errorMsg.classList.remove("hidden");
            errorMsg.scrollIntoView({behavior: "smooth"});
        } else {
            const emailValidation = validateEmail(email.value.normalize());

            if (emailValidation) {
                e = email.value.normalize();
                p = password.value.normalize();

                // Submit button effect
                loginSubmitBtn.classList.remove("bg-indigo-500");
                loginSubmitBtn.classList.remove("ripple__button");
                loginSubmitBtn.classList.add("bg-slate-700");
                loginSubmitBtn.disabled = true;
                loginBtnSpinner.classList.remove("hidden");

                loginAccount(e, p);
            } else {
                errorMsg.innerText = "Please enter a valid email address!";
                errorMsg.classList.remove("hidden");
                errorMsg.scrollIntoView({behavior: "smooth"});
            }
        }
    })

    async function loginAccount(email, password) {
        const CSRFTOKEN = getCookie("csrftoken");

        let formData = new FormData();
        formData.append("email", email);
        formData.append("password", password);

        await fetch("/account/user-login/", {
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
            } else if (!data.error && data.invalid_user) {
                errorMsg.innerText = "Invalid user credential!";
                errorMsg.classList.remove("hidden");
                errorMsg.scrollIntoView({behavior: "smooth"});
            } else if (!data.error && data.user_login) {
                window.location.href = "/";
            }
        }).catch(err => console.error(err));

        // Submit button effect
        loginSubmitBtn.classList.add("bg-indigo-500");
        loginSubmitBtn.classList.add("ripple__button");
        loginSubmitBtn.classList.remove("bg-slate-700");
        loginSubmitBtn.disabled = false;
        loginBtnSpinner.classList.add("hidden");
    }
})