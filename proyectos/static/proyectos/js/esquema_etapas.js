$(document).ready(function() {
    // Barra de progreso
    var progress = Math.round(parseFloat($("#progressbar").attr("value")));
    $("#progressbar").progressbar({ value: progress });
    $(".milestone_progressbar").each(function() {
        progress = Math.round(parseFloat($(this).attr("value")));
        $(this).progressbar({ value: progress });
    });

    $(".link_avance").click(function() {
        $(this).next(".avance").toggle('slow');
    });
    $(".show").show();

    // Sliders
    var controls_container;
    $(".slider-tab").each(function() {
        controls_container = $(this).next();
        $(this).OverSlider({controls_container: controls_container});
        controls_container.children(".prev").addClass("span-4");
        controls_container.children(".next").addClass("span-4 right last");
    })
});