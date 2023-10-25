
// Function to navigate to a specified URL
function navigateTo(url) {
    window.location.href = url;  // redirect the page to the specified URL
}

// Function to authenticate the user
function authenticate() {
    // Get the email and password input fields
    const emailInput = document.getElementById("email").value;
    const passwordInput = document.getElementById("password").value;

    // AJAX request to the server to authenticate the user
    $.ajax({
        url: "/login",  // the endpoint to authenticate the user
        method: "POST",  // HTTP method
        headers: { "Content-Type": "application/json" },  // set the content type of the request
        data: JSON.stringify({  // convert the data to JSON format
            email: emailInput,
            password: passwordInput,
        }),
        success: response => {  // function to execute if the request is successful
            if (response.code === 0) {  // if the server returned code 0 (success)
                localStorage.setItem("token", response.token);  // store the token in local storage
                navigateTo("/history");  // navigate to the chat page
            } else {
                window.alert(response.msg);  // display the server's response message
            }
        },
        error: error => {  // function to execute if the request fails
            window.alert(error.msg);  // display the error message
        },
    });
}
// Check if the user is already logged in
const token = localStorage.getItem("token");

// AJAX request to the server to verify if the user is logged in
$.ajax({
    url: "/check_login",  // the endpoint to verify login
    method: "GET",  // HTTP method
    headers: { Authorization: `Bearer ${token}` },  // Authorization header with the token
    success: response => {  // function to execute if the request is successful
        console.log(response);  // log the response to the console
        navigateTo("/history");  // navigate to the chat page
    },
    error: error => {  // function to execute if the request fails
        localStorage.clear();  // clear local storage
    },
});
