// Document ready event that triggers when the DOM is fully loaded and ready
$(document).ready(() => {
    // Fetching the form with id 'register-form' from the DOM
    const registerForm = $("#register-form");

    // Fetching the alert box with id 'alert-box' from the DOM
    const alertBox = $("#alert-box");

    // Fetching the alert message with id 'alert-message' from the DOM
    const alertMessage = $("#alert-message");

    // Handling the form submission event
    registerForm.submit(event => {
        // Preventing the default form submission event
        event.preventDefault();

        // Collecting form data into an object
        const formData = {
            first_name: $("#first_name").val(),
            last_name: $("#last_name").val(),
            phone: $("#phone").val(),
            email: $("#email").val(),
            password: $("#password").val()
        };

        // Making an AJAX call to the '/users' route with the form data
        $.ajax({
            url: "/users",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(formData),
            // On success of the AJAX call, this function will be executed
            success: response => {
                // Logging the message received from the server to the console
                console.log(response.msg);

                // If the code in the response is 0, store the token in local storage and redirect the user to the '/chat' page
                if (response.code === 0) {
                    localStorage.setItem('token', response.token);
                    window.location.href = "/history";
                }
            },
            // On error of the AJAX call, this function will be executed
            error: error => {
                // If the error status is 400 and the error code is -1 or -2, display the error message in the alert box
                if (error.status === 400 && (error.responseJSON.code === -1 || error.responseJSON.code === -2)) {
                    alertMessage.text(error.responseJSON.msg);
                    alertBox.show();
                }
                // If the error status is 409 and the error code is -3, display the error message in the alert box
                else if (error.status === 409 && error.responseJSON.code === -3) {
                    alertMessage.text(error.responseJSON.msg);
                    alertBox.show();
                }
            },
        });
    });

    // Handling the alert box close event, when it's closed, the page will be reloaded
    alertBox.on('closed.bs.alert', () => {
        location.reload();
    });
});
