$(document).ready(function () {
    $('.accordion-content').hide();

    $('.accordion-header').click(function () {
        $(this).siblings('.accordion-content').find('.accordion-content').hide();
        $(this).children('.arrow').toggleClass('rotated');
        $(this).siblings('.accordion-content').slideToggle();
    });
});