$(document).ready(function () {
    $('.accordion-content').hide();

    $('.accordion-header').click(function () {
        $(this).siblings('.accordion-content').find('.accordion-content').hide();
        $(this).siblings('.accordion-content').find('.arrow').removeClass('rotated');
        $(this).children('.arrow').toggleClass('rotated');
        $(this).siblings('.accordion-content').slideToggle();
    });
});