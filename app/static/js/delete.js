$(document).ready(function() {
    $('form').on('submit', function(e) {
        e.preventDefault();
        var objectType;
        var objectId;

        objectType = $('#object-type').val();
        objectId = $('#object-id').val();

        DeleteObject(objectType, objectId);
    })

});

function DeleteObject(objectType, objectId) {

        $.ajax({
            type: "DELETE",
            url: "api/"+objectType+"/delete/"+objectId,
            contentType: "application/json; charset=UTF-8",
            dataType: "json",
            success: function(response) {
                window.location = '/home'
            },
            error: function(error) {
                console.log(error);
                result = false;
            }
        });
}
