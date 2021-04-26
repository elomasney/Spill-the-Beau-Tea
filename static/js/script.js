//Toggles the tooltip on the repurchase icon in reviews
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

//Collapsable favourites accordion menu
$('.collapse').collapse()

// Toggles favourites icon button on click
$('.far.fa-heart').click(function () {
    $('.far.fa-heart').toggleClass('far fa-heart fas fa-heart')

});