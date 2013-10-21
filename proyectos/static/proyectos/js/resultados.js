function mostrar_busqueda(id) {
    url = "/proyectos/" + id;
    window.location.href = url;
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
function addCommas(nStr)
{
    nStr += '';
    var x = nStr.split('.');
    var x1 = x[0];
    var x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2;
}
$(document).ready(function() {
    // Búsqueda de proyectos
    $('#id_nombre').SearchBox("/proyectos/json_fast_proyectos/", mostrar_busqueda, {box_img: null});
    // Ya se ha seleccionado una región
    if(has_location) {
        $("#id_hi_lat").val(hi_lat);
        $("#id_hi_lon").val(hi_lon);
        $("#id_lo_lat").val(lo_lat);
        $("#id_lo_lon").val(lo_lon);
        $("#id_location").val(location);
    }
    // Slider de precios
    $("#slider-range").slider({
        range: true,
        step: 100,
        min: min_renta,
        max: max_venta,
        values: [value_min, value_max],
        slide: function(event, ui) {
            $("#id_max_precio").val(ui.values[0]);
            $("#id_min_precio").val(ui.values[1]);
            $(".fucsia_box").html("$" + addCommas(ui.values[0]));
            $(".gris_box").html("$" + addCommas(ui.values[1]));
        }
    });
    $(".fucsia_box").html("$" + addCommas($("#slider-range").slider("values", 0)));
    $(".gris_box").html("$" + addCommas($("#slider-range").slider("values", 1)));

    loadResultsMap("map_resultados", results, bounds);

    $("#popup_results_map").jqm({
        trigger: $('.results_link')
    });

    $("input[name=tipo]").change(function() {
        if($(this).attr("id") == "id_tipo_0") {
            $("#slider-range").slider("option", "min", min_renta);
            $("#slider-range").slider("option", "max", max_renta);
        }
        if($(this).attr("id") == "id_tipo_1") {
            $("#slider-range").slider("option", "min", min_venta);
            $("#slider-range").slider("option", "max", max_venta);
        }
        if($(this).attr("id") == "id_tipo_2") {
            $("#slider-range").slider("option", "min", min_renta);
            $("#slider-range").slider("option", "max", max_venta);
        }
        $(".fucsia_box").html("$" + addCommas($("#slider-range").slider("values", 0)));
        $(".gris_box").html("$" + addCommas($("#slider-range").slider("values", 1)));
    });

    $('.results_link').click(function() {
        loadResultsMap("map_resultados_big", results, bounds);
    });

    $('.link_afiliar').click(function() {
        var link = $(this);
        var request = $.ajax({
            url: url,
            type: "GET",
            data: {usuario: usuario, proyecto: $(this).attr("proyecto_id")},
            dataType: "html"
        });

        request.done(function(msg) {
            var data = jQuery.parseJSON(msg);
            if(data.status) {
                link.parent().html("<span>Ya está afiliado</span>");
            }
        });
    });

    $("#popup_preview_map").jqm({
        trigger: $(".link_mapa_proyecto")
    });
    $(".link_mapa_proyecto").click(function() {
        loadPreviewMap("map_preview", $(this).attr("latitud"), $(this).attr("longitud"));
    });

    $("#ubicacion_map").jqm({
        trigger: $(".get_ubicacion")
    });
    var area = new google.maps.Rectangle();
    $(".get_ubicacion").click(function() {
        MapArea("map_area", area);
    });

    $("#get_bounds").click(function() {
        $("#id_hi_lat").val(area.getBounds().getNorthEast().lat());
        $("#id_hi_lon").val(area.getBounds().getNorthEast().lng());
        $("#id_lo_lat").val(area.getBounds().getSouthWest().lat());
        $("#id_lo_lon").val(area.getBounds().getSouthWest().lng());
        $("#id_location").val(area.getBounds().getCenter().toUrlValue());
        $("#id_ubicacion").val("Búsqueda por área");
        $("#id_ubicacion").attr("disabled", true);
        $("#ubicacion_map").jqmHide();
    });

    $("#busqueda_form").submit(function() {
        geocode_location();
        return false;
    });

    $(".submit_buscar").click(function() {
        $("#busqueda_form").submit();
    });

    $(".contacto_link").click(function() {
        $("#id_proyecto_contacto").val($(this).attr("proyecto"));
        $("#contacto_form").submit();
    });
});