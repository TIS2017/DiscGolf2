$(document).ready(function() {

    $(".nav_item").click(function() {
        $(this).addClass("active");
    });

    $('.clockpicker').clockpicker({
        placement: 'top',
        align: 'left',
        donetext: 'Done'
    });
});