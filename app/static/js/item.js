$(document).ready(function() {
    $('form').on('submit', function(e) {
        e.preventDefault();
        var itemId;
        var categoryId;
        var itemName;
        var itemDescription;

        itemId = $('#item-id').val();
        categoryId = $('#category-name').val();
        itemName = $('#item-name').val();
        itemDescription = $('#item-description').val();
        UpdateItem(itemId, categoryId, itemName, itemDescription);
    })

});

function UpdateItem(itemId, categoryId, itemName, itemDescription) {
    var requestData;
    request_data = {
        "item_id": itemId,
        "category_id": categoryId,
        "item_name": itemName,
        "item_description": itemDescription,
    };
    console.log(request_data)
        $.ajax({
            type: "PUT",
            url: "api/item/update",
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
