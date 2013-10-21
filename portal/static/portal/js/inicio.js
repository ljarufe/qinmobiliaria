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
    // Mensaje de cuenta verificada
    if(getURLParameter("uc_verified") != "null") {
        $("#uc_verified").jqmShow();
    }
    // Cuadro de búsqueda
    $('#id_nombre').SearchBox("/proyectos/json_fast_proyectos/", mostrar_busqueda, {box_img: null});
    $('#search_box_input').val("Nombre");
    $("#search_box_input").click(function() {
        $(this).val("");
    });
    $("#search_box_input").focusout(function() {
        $(this).val("Nombre");
    });
    // Rango de precios
    $("#slider-range").slider({
        range: true,
        step: 100,
        min: min_renta,
        max: max_venta,
        values: [min_renta, max_venta],
        slide: function(event, ui) {
            $("#id_min_precio").val(ui.values[0]);
            $("#id_max_precio").val(ui.values[1]);
            $(".fucsia_box").html("$" + addCommas(ui.values[0]));
            $(".gris_box").html("$" + addCommas(ui.values[1]));
        }
    });
    $(".fucsia_box").html("$" + addCommas($("#slider-range").slider("values", 0)));
    $(".gris_box").html("$" + addCommas($("#slider-range").slider("values", 1)));
    $("input[name=tipo]").change(function() {
        // TODO: Mover los rangos a los extremos
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
    // Mapa de resultados
    $("#id_ubicacion").val("Búsqueda por área");
    $("#id_ubicacion").attr("disabled", true);
    var start_marker_pos = new google.maps.LatLng(-15.400728,-72.663574);
    var end_marker_pos = new google.maps.LatLng(-16.817687,-70.466309);
    var area = new google.maps.Rectangle();

    $(".get_ubicacion").click(function() {
        $("#ubicacion_map").jqmShow();
        MapArea("map_area", area, start_marker_pos, end_marker_pos);
    });
    // Búsqueda por ubicación
    $("#get_bounds").click(function() {
        $("#id_hi_lat").val(area.getBounds().getSouthWest().lat());
        $("#id_hi_lon").val(area.getBounds().getNorthEast().lng());
        $("#id_lo_lat").val(area.getBounds().getNorthEast().lat());
        $("#id_lo_lon").val(area.getBounds().getSouthWest().lng());
        $("#id_location").val(area.getBounds().getCenter().toUrlValue());
        $("#ubicacion_map").jqmHide();
    });
    // Formulario de búsqueda
    $("#busqueda_form").submit(function() {
        geocode_location();
        return false;
    });
    $(".submit_buscar").click(function() {
        $("#busqueda_form").submit();
    });
    // Slider de proyectos
    var old_position = 1;
    $(".slider-trigger").click(function() {
        $(".slider-activo").removeClass("slider-activo");
        var trigger = $(this);
        trigger.addClass("slider-activo");
        var new_position = trigger.attr("position");
        var desp = 320*(new_position - old_position);
        if(desp > 0) {
            $(".slider-tab > div").animate({"scrollTop": "+=" + desp}, 400,
                function() {
                    window.open(trigger.attr("href"), '_self', false);
                });
        }
        else{
            $(".slider-tab > div").animate({"scrollTop": "-=" + -1*desp}, 400,
                function() {
                    window.open(trigger.attr("href"), '_self', false);
                });
        }
        old_position = new_position;
    });
    var timer = setInterval(function() {
        var old_activo = $(".slider-activo");
        $(".slider-activo").removeClass("slider-activo");
        if(old_position < 5) {
            old_activo.next().addClass("slider-activo");
            $(".slider-tab > div").animate({"scrollTop": "+=" + 320}, 400);
            old_position++;
        }
        else {
            old_activo.prev().prev().prev().prev().addClass("slider-activo");
            $(".slider-tab > div").animate({"scrollTop": "-=" + 320*4}, 400);
            old_position = 1;
        }
    }, 8000);
    // Tooltips
    $('#search_box_input').tipsy({
            fallback: "Escriba parte del nombre y elija entre los proyectos",
            gravity: 'w',
            fade: true,
            trigger: 'focus'}
    );
    // Popins
    $("#ubicacion_map").jqm();
});