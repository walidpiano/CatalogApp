$(document).ready(function() {
    $('form').on('submit', function(e) {
        e.preventDefault();
        var categoryId;
        var categoryName;
        categoryId = $('#category-id').val();
        categoryName = $('#category-name').val();
        UpdateCategory(categoryId, categoryName);
    })

});

function UpdateCategory(categoryId, categoryName) {
    var requestData;
    requestData = {
        "category_id": categoryId,
        "category_name": categoryName,
    };
    console.log(requestData)
        $.ajax({
            type: "PUT",
            url: "api/category/update",
            data: JSON.stringify(requestData),
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
