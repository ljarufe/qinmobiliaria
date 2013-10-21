function mostrar_busqueda(slug) {
    url = "/" + slug + "/";
    window.location.href = url;
}

function getURLParameter(name) {
    return decodeURI((new RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,null])[1]);
}

function geocode_location() {
    var geocoder = new google.maps.Geocoder();

    var address = $("#id_ubicacion").val();
    geocoder.geocode({'address': address}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var bounds = results[0].geometry.viewport.toUrlValue().split(",");
            $("#id_hi_lat").val(bounds[0]);
            $("#id_hi_lon").val(bounds[1]);
            $("#id_lo_lat").val(bounds[2]);
            $("#id_lo_lon").val(bounds[3]);
            $("#id_location").val(results[0].geometry.location.toUrlValue());
            $('#busqueda_form').unbind('submit');
            $('#busqueda_form').submit();
        }
        else {
            $('#busqueda_form').unbind('submit');
            $('#busqueda_form').submit();
        }
    });
}

$(document).ready(function() {
    if(active_user && getURLParameter("next") != "null") {
        window.open(getURLParameter("next"), '_self', false);
    }
    $("#login").jqm({
        trigger: $(".login_link")
    });
    $('.close_popin').click(function() {
        $('.jqmWindow').jqmHide();
    });
    $("#uc_verified").jqm({
	    trigger: ''
    });
    // Menu desplegable de un usuario logeado
    var logged_show = false;
    $('.logged_user').click(function() {
        if(logged_show) {
            $(this).next('.menu_user').slideUp(400);
            logged_show = false;
        }
        else {
            $(this).next('.menu_user').slideDown(400);
            logged_show = true;
        }
    });
    // Menu desplegable de rubros-proyectos
    $(function () {
        $(".dropdown").each(function () {
            $(this).parent().eq(0).hover(function () {
                $(".dropdown:eq(0)", this).slideDown();
            }, function () {
                $(".dropdown:eq(0)", this).slideUp(10);
            });
        });
    });
    $('.submenu_proy').mouseleave(function() {
        $(this).hide(400);
    });
    // Menu de entrada al chat
    $(".chat_trigger").click(function() {
        if(chat_show) {
            $(this).next("#chat_form").hide(400);
            chat_show = false;
        }
        else {
            $(this).next("#chat_form").show(400);
            chat_show = true;
        }
    });
});
