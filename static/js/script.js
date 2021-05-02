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

//Popup confirm delete category on link click
$(function () {
    $('.category_delete').on('click', function () {
        let delete_url = $(this).attr('data-href');
        confirm_delete_category(delete_url);
    });
});

//Confirm Delete Category
function confirm_delete_category(delete_url) {

    Swal.fire({
        title: 'Delete this Category?',
        text: "This category will be permanently deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#fafd42',
        cancelButtonColor: '#15bce2',
        confirmButtonText: 'Yes, delete it!',

    }).then((result) => {
        if (result.isConfirmed) {

            window.location.href = delete_url

            Swal.fire(
                'Deleted!',
                'This category has been deleted.',
                'success');

        }
    })
};

//Popup confirm delete product on link click
$(function () {
    $('.product_delete').on('click', function () {
        let delete_url = $(this).attr('data-href');
        confirm_delete_product(delete_url);
    });
});

//Confirm Delete Product
function confirm_delete_product(delete_url) {

    Swal.fire({
        title: 'Delete this Product?',
        text: "This product will be permanently deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#fafd42',
        cancelButtonColor: '#15bce2',
        confirmButtonText: 'Yes, delete it!',

    }).then((result) => {
        if (result.isConfirmed) {

            window.location.href = delete_url

            Swal.fire(
                'Deleted!',
                'This product has been deleted.',
                'success');

        }
    })
};

//Popup confirm delete reviews on link click
$(function () {
    $('.review_delete').on('click', function () {
        let delete_url = $(this).attr('data-href');
        confirm_delete_review(delete_url);
    });
});

//Confirm Delete Review
function confirm_delete_review(delete_url) {

    Swal.fire({
        title: 'Delete this Review?',
        text: "This review will be permanently deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#fafd42',
        cancelButtonColor: '#15bce2',
        confirmButtonText: 'Yes, delete it!',

    }).then((result) => {
        if (result.isConfirmed) {

            window.location.href = delete_url

            Swal.fire(
                'Deleted!',
                'This review has been deleted.',
                'success');

        }
    })
};

//Popup confirm delete user account on link click
$(function () {
    $('.account_delete').on('click', function () {
        let delete_url = $(this).attr('data-href');
        confirm_delete_account(delete_url);
    });
});

//Confirm Delete Account
function confirm_delete_account(delete_url) {

    Swal.fire({
        title: 'Delete your account?',
        text: "Your account will be permanently deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#fafd42',
        cancelButtonColor: '#15bce2',
        confirmButtonText: 'Yes, delete it!',

    }).then((result) => {
        if (result.isConfirmed) {

            window.location.href = delete_url

            Swal.fire(
                'Deleted!',
                'Your account has been deleted.',
                'success');

        }
    })
};

//Change main container height on 404 page only
$(function () {
    if (window.location.pathname == "/404") {
        $('#main-container').height('100vh');
    }
});