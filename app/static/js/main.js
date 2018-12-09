$(document).ready(function() {

    GetLastItems();

});



function GetLastItems() {

    $.ajax({
        type: "GET",
        url: "/api/last/items",
        dataType: "json",
        success: function(response) {
            var item_link;
            $.each(response, function (index, item) {
                item_link = item.item_id == '#'? 'items' : item.item_name;

                var htmlCategory = '<div id="category-" class="items-list"><a href="catalog/'+item.category_name+'/items"><div class="category">'+item.category_name+'</div></a>'
                var htmlItem = '<a href="catalog/'+item.category_name+'/'+item_link+'"><div class="category">'+item.item_name+'</div></a></div><hr/>';
                $('#items').append(htmlCategory+htmlItem);
            });
        }
    });
}
