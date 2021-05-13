/* jshint esversion: 8 */

//Toggles the tooltip on the repurchase icon in reviews
$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();

});

// Toggles favourites icon button on click
$('.far.fa-heart').click(function () {
    $('.far.fa-heart').toggleClass('far fa-heart fas fa-heart');

});

/**
 * @function - displays sweetalert confirmation on 'delete category' button
 */
//Popup confirm delete category on link click
$(function () {
    $('.category_delete').on('click', function () {
        let delete_url = $(this).attr('data-href');
        confirm_delete_category(delete_url);
    });
});

/**
 * @function confirm_delete_category - displays sweetalert popup
 * @param delete_url - path to delete a category from the db
 * Asks user to confirm if they want to delete a category from the database
 * On confirmation the category is deleted from the db
 */
//Confirm Delete Category
function confirm_delete_category(delete_url) {

    Swal.fire({
        title: 'Delete this Category?',
        text: "This category will be permanently deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#fbec5d',
        cancelButtonColor: '#a0dfdf	',
        confirmButtonText: 'Yes, delete it!',

    }).then((result) => {
        if (result.isConfirmed) {

            window.location.href = delete_url;

            Swal.fire(
                'Deleted!',
                'This category has been deleted.',
                'success');

        }
    });
}

/**
 * @function - displays sweetalert confirmation on 'delete product' button
 */
//Popup confirm delete product on link click
$(function () {
    $('.product_delete').on('click', function () {
        let delete_url = $(this).attr('data-href');
        confirm_delete_product(delete_url);
    });
});

/**
 * @function confirm_delete_product - displays sweetalert popup
 * @param delete_url - path to delete a product from the db
 * Asks user to confirm if they want to delete a product from the database
 * On confirmation the product is deleted from the db
 */
//Confirm Delete Product
function confirm_delete_product(delete_url) {

    Swal.fire({
        title: 'Delete this Product?',
        text: "This product will be permanently deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#fbec5d',
        cancelButtonColor: '#a0dfdf	',
        confirmButtonText: 'Yes, delete it!',

    }).then((result) => {
        if (result.isConfirmed) {

            window.location.href = delete_url;

            Swal.fire(
                'Deleted!',
                'This product has been deleted.',
                'success');

        }
    });
}

/**
 * @function - displays sweetalert confirmation on 'delete review' button
 */
//Popup confirm delete reviews on link click
$(function () {
    $('.review_delete').on('click', function () {
        let delete_url = $(this).attr('data-href');
        confirm_delete_review(delete_url);
    });
});

/**
 * @function confirm_delete_review - displays sweetalert popup
 * @param delete_url - path to delete a review from the db
 * Asks user to confirm if they want to delete a review from the database
 * On confirmation the review is deleted from the db
 */
//Confirm Delete Review
function confirm_delete_review(delete_url) {

    Swal.fire({
        title: 'Delete this Review?',
        text: "This review will be permanently deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#fbec5d',
        cancelButtonColor: '#a0dfdf	',
        confirmButtonText: 'Yes, delete it!',

    }).then((result) => {
        if (result.isConfirmed) {

            window.location.href = delete_url;

            Swal.fire(
                'Deleted!',
                'This review has been deleted.',
                'success');

        }
    });
}

/**
 * @function - displays sweetalert confirmation on 'delete account' button
 */
//Popup confirm delete user account on link click
$(function () {
    $('.account_delete').on('click', function () {
        let delete_url = $(this).attr('data-href');
        confirm_delete_account(delete_url);
    });
});

/**
 * @function confirm_delete_account - displays sweetalert popup
 * @param delete_url - path to delete a user account from the db
 * Asks user to confirm if they want to delete a user account from the database
 * On confirmation the user account is deleted from the db
 */
//Confirm Delete Account
function confirm_delete_account(delete_url) {

    Swal.fire({
        title: 'Delete your account?',
        text: "Your account will be permanently deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#fbec5d',
        cancelButtonColor: '#a0dfdf	',
        confirmButtonText: 'Yes, delete it!',

    }).then((result) => {
        if (result.isConfirmed) {

            window.location.href = delete_url;

            Swal.fire(
                'Deleted!',
                'Your account has been deleted.',
                'success');

        }
    });
}

/**
 * @function - displays sweetalert confirmation on 'delete category' button
 */
//Popup confirm delete category on link click
$(function () {
    $('.delete-comment').on('click', function () {
        let delete_url = $(this).attr('data-href');
        confirm_delete_comment(delete_url);
    });
});

/**
 * @function confirm_delete_comment - displays sweetalert popup
 * @param delete_url - path to delete a feedback entry from the db
 * Asks user to confirm if they want to delete a feedback entry from the database
 * On confirmation the comment is deleted from the db
 */
//Confirm Delete Feedback 
function confirm_delete_comment(delete_url) {

    Swal.fire({
        title: 'Delete this Comment?',
        text: "This feedback will be permanently deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#fbec5d',
        cancelButtonColor: '#a0dfdf	',
        confirmButtonText: 'Yes, delete it!',

    }).then((result) => {
        if (result.isConfirmed) {

            window.location.href = delete_url;

            Swal.fire(
                'Deleted!',
                'This comment has been deleted.',
                'success');

        }
    });
}

/**
 * @function - changes main container height on 404 error page
 * Sets body padding to zero on 404 error page
 */
//Change main container height on 404 page only
$(function () {
    if (window.location.pathname == "/404" ) {
        $('#main-container').height('100vh');
        $("body").css("padding-top", "0");

    }
});

/**
 * @function - adds slide up/slide down animation to flash messages
 * Sets timeout for 5 seconds
 */
//Timeout for flash messages
$('.flashes').hide().slideDown('slow');
setTimeout(function(){
    $('.flashes').slideUp('slow');
}, 5000);

//Set copyright year dynamically
$('.copyright-date').text(new Date().getFullYear());