$(document).ready(function() {
    $('.link_suscribir').click(function() {
        var rubro = $(this).attr("rubro");
        var request = $.ajax({
            url: url,
            type: "GET",
            data: {rubro: rubro},
            dataType: "html"
        });
        request.done(function(msg) {
            var data = jQuery.parseJSON(msg);
            if(data.status) {
                $(".link_suscribir").html('<span>Ya está suscrito</span>');
            }
        });
    });

    $(".registro_link").click(function() {
        $("#registro_form").submit();
    });
});