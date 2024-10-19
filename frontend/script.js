$(document).ready(function() {
    $('#input-form').on('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = $(this).serialize(); // Collect form data as a query string

        $.ajax({
            url: 'http://localhost:5000/recommend', // the backend url
            type: 'POST',
            data: formData,
            success: function(data) {
                $('#message').text(data.message || 'Recommendations received!');
            },
            error: function(xhr) {
                $('#message').text(xhr.responseJSON.error || 'Request failed.');
            }
        });
    });
});