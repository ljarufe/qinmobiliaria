$(document).ready(function() {
    // Quitar la suscripción a un rubro
    $(".de-suscribir").click(function() {
        var link = $(this);
        var request = $.ajax({
            url: url_desuscribir,
            type: "GET",
            data: {id_rubro: link.attr("rubro")},
            dataType: "html"
        });
        request.done(function(msg) {
            var data = jQuery.parseJSON(msg);
            if(data.status) {
                link.parent().parent().remove();
            }
        });
    });
    // Áreas de interés
    var map_options = {
        zoom: 10,
        center: new google.maps.LatLng(-16.398748,-71.536961),
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_area"), map_options);
    var areas = [];
    var area_count = 0;
    var marker_options = {
        map: map,
        draggable: true
    };
    for(i = 0; i < num_form_areas; i++) {
        areas[area_count] = {stage: 1};
        areas[area_count].instance = true;
        areas[area_count].id = form_areas[i].id;
        areas[area_count].start_marker = new google.maps.Marker(marker_options);
        areas[area_count].start_marker.setPosition(new google.maps.LatLng(form_areas[i].high_latitud, form_areas[i].low_longitud));
        areas[area_count].end_marker = new google.maps.Marker(marker_options);
        areas[area_count].end_marker.setPosition(new google.maps.LatLng(form_areas[i].low_latitud, form_areas[i].high_longitud));
        areas[area_count].area = new google.maps.Rectangle({map: map});
        areas[area_count].area.setBounds(new google.maps.LatLngBounds(
            areas[area_count].start_marker.getPosition(),
            areas[area_count].end_marker.getPosition()
        ));
        google.maps.event.addListener(areas[area_count].start_marker, 'drag',
            (function(area_count) {
                return function() {
                    refreshArea(area_count);
                    refreshCloseMarker(area_count);
                }
            })(area_count)
        );
        google.maps.event.addListener(areas[area_count].end_marker, 'drag',
            (function(area_count) {
                return function() {
                    refreshArea(area_count);
                    refreshCloseMarker(area_count);
                }
            })(area_count)
        );
        areas[area_count].close_marker = new google.maps.Marker(
            {
                map: map,
                draggable: false,
                position: new google.maps.LatLng(
                    areas[area_count].start_marker.getPosition().lat(),
                    areas[area_count].end_marker.getPosition().lng()
                )
            }
        );
        google.maps.event.addListener(areas[area_count].close_marker, 'click',
            (function(area_count) {
                return function() {
                    areas[area_count].start_marker.setMap(null);
                    areas[area_count].end_marker.setMap(null);
                    areas[area_count].close_marker.setMap(null);
                    areas[area_count].area.setMap(null);
                    areas[area_count].stage = false;
                    $("#id_form-" + area_count + "-delete").val("True");
                }
            })(area_count)
        );
        area_count++;
    }
    areas[area_count] = {stage: 0};
    MapAreas(map, areas, area_count);
    // Enviar los datos
    $('#id_form-TOTAL_FORMS').val(0);
    $("#int_form").submit(function() {
        area_count = 0;
        var usuario = "{{ user.get_full_name }}";
        for(var i = 0; i < areas.length; i++) {
            if(areas[i].instance) {
                if(areas[i].stage) {
                    $("#id_form-" + area_count + "-high_latitud").val(areas[i].start_marker.getPosition().lat());
                    $("#id_form-" + area_count + "-high_longitud").val(areas[i].end_marker.getPosition().lng());
                    $("#id_form-" + area_count + "-low_latitud").val(areas[i].end_marker.getPosition().lat());
                    $("#id_form-" + area_count + "-low_longitud").val(areas[i].start_marker.getPosition().lng());
                }
                area_count++;
            }
            else if(areas[i].stage) {
                var form = '<input type="hidden" name="form-' + area_count + '-nombre" id="id_form-' + area_count + '-nombre" value="' + usuario + "-" + area_count + '">' +
                    '<input type="hidden" name="form-' + area_count + '-high_latitud" id="id_form-' + area_count + '-high_latitud" value="' + areas[i].start_marker.getPosition().lat() + '">' +
                    '<input type="hidden" name="form-' + area_count + '-high_longitud" id="id_form-' + area_count + '-high_longitud" value="' + areas[i].end_marker.getPosition().lng() + '">' +
                    '<input type="hidden" name="form-' + area_count + '-low_latitud" id="id_form-' + area_count + '-low_latitud" value="' + areas[i].end_marker.getPosition().lat() + '">' +
                    '<input type="hidden" name="form-' + area_count + '-low_longitud" id="id_form-' + area_count + '-low_longitud" value="' + areas[i].start_marker.getPosition().lng() + '">';
                $("#id_form-MAX_NUM_FORMS").after(form);
                area_count++;
            }
        }
        $('#id_form-TOTAL_FORMS').val(String(area_count));
    });
});