$(document).ready(function() {
    $('#upload-form').on('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(this); // Collect form data

        $.ajax({
            url: 'http://localhost:5000/upload', // Backend URL
            type: 'POST',
            data: formData,
            processData: false, // Prevent jQuery from automatically transforming the data into a query string
            contentType: false, // Set to false to let the browser set the content type
            success: function(data) {
                $('#message').text(data.message || 'Upload successful!');
            },
            error: function(xhr) {
                $('#message').text(xhr.responseJSON.error || 'Upload failed.');
            }
        });
    });
});