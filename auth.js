document.getElementById("loginForm").addEventListener("submit", function(e) {
    e.preventDefault();

    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value.trim();
    

    loginUser(email, password)
    .then(data => {

        console.log("API RESPONSE:", data);

        // ✅ MAIN FIX HERE
        if (data.result && data.result > 0) {

            // SAVE SESSION
           localStorage.setItem("userEmail", email);
           localStorage.setItem("isLoggedIn", "true");

           
// OPTIONAL (if you have name)
localStorage.setItem("userName", email); 

            alert("Login Successful ✅");

            // REDIRECT
            window.location.href = "index.html";

        } else {
            document.getElementById("msg").innerText =
                "Wrong Email or Password ❌";
        }

    })
    .catch(err => {
        console.error(err);
        document.getElementById("msg").innerText =
            "Server Error ⚠️";
    });
});

