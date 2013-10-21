$(document).ready(function() {
    // Colocar la presentación al centro de la pantalla
    var winWidth = 0;
    var imageWidth = $('#web_proyecto').width();
    var lifeBorders = function (){
        winWidth = ($(window).width() - imageWidth)/2;
        $('#web_proyecto').css("left", winWidth.toString()+"px");
    };
    lifeBorders();
    $(window).resize(lifeBorders);
    // Pestañas
    $("#tabs").tabs();
    // Slider
    var controls_container = $(".slider-tab").next();
    $(".slider-tab").OverSlider({controls_container: controls_container});
    controls_container.children(".prev").addClass("span-4");
    controls_container.children(".next").addClass("span-4 right last");
    // Barra de progreso
    var progress = Math.round(parseFloat($("#progressbar").attr('value')));
    $("#progressbar").progressbar({ value: progress });
    // Mapa con las referencias
    $("#tab_ubicacion").click(function() {
        loadReferencesMap("mapa_ubicacion", latitud, longitud, references);
    });
    // Afiliar a este rubro al cliente
    $('.link_afiliar').click(function() {
        var link = $(this);
        var request = $.ajax({
            url: url,
            type: "GET",
            data: {proyecto: proyecto},
            dataType: "html"
        });
        request.done(function(msg) {
            var data = jQuery.parseJSON(msg);
            if(data.status) {
                link.parent().html("<span>Ya está afiliado</span>");
            }
        });
    });
    // Web del proyecto
    var jqmOpen = function(hash){
        hash.w.show();
        $("#web_proyecto > iframe").attr("src", web_proyecto_url);
    };
    var jqmClose = function(hash) {
        hash.w.fadeOut('2000',function() {
            hash.o.remove();
        });
        $("#web_proyecto > iframe").attr("src", "");
    };
    $('#web_proyecto').jqm({
        onShow: jqmOpen,
        onHide: jqmClose,
        trigger: $("#web_proyecto_link")
    });
    if(web_proyecto_url != "" && getURLParameter("web_proyecto") == 1) {
        $("#web_proyecto").jqmShow();
    }
    // Redireccionar contacto
    $("#contacto_menu_base").replaceWith($('<span class="contacto_link login_link">Contacto</span>'));
    $(".contacto_link").click(function() {
        $("#contacto_form").submit();
    });
});
