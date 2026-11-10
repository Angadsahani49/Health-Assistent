// database.js

const BASE_URL = "https://oracleapex.com/ords/angad123/users_IDT_2";

// SIGNUP FUNCTION
function signupUser(fullname, email, password) {
    return fetch(BASE_URL + "/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            fullname: fullname,
            email: email,
            password: password
        })
    })
    .then(res => res.json());
}

// FIXED LOGIN FUNCTION (Oracle uses "username" instead of "email")


function loginUser(email, password) {
    return fetch(BASE_URL + "/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,      // ✅ MATCH POSTMAN
            password: password
        })
    })
    .then(res => res.json());
}