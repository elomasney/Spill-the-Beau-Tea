/* jshint esversion: 8 */

//Global Variables
const delete_category_url = "delete_category/category_id = category._id"




//Toggles the tooltip on the repurchase icon in reviews
$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();

});

//Collapsable favourites accordion menu
$('.collapse').collapse();

// Toggles favourites icon button on click
$('.far.fa-heart').click(function () {
    $('.far.fa-heart').toggleClass('far fa-heart fas fa-heart')

});

//Confirm Delete Category
function confirm_delete() {
    Swal.fire({
        title: 'Delete this Category?',
        text: "This category will be permanently deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'

    }).then((result) => {
        if (result.isConfirmed) {

            let categoryId = ` ${
                category.category_id
            }.toString()`
            window.location.href = "/delete_category/categoryId";

            Swal.fire(
                'Deleted!',
                'This category has been deleted.',
                'success');

        }
    })
};