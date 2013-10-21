var main_map;
var preview_map;
var result_map;
var references_map;
var main_marker;
var preview_marker;
var place_marker;

function loadMap(latitud, longitud) {
    var geocoder = new google.maps.Geocoder();
    
    var myLatlng;
    if(latitud && longitud) {
        myLatlng = new google.maps.LatLng(latitud.replace(",", "."), longitud.replace(",", "."));
    } else {
        myLatlng = new google.maps.LatLng(-16.398748,-71.536961);
    }

    var myOptions = {
        zoom: 12,
        center: myLatlng,
        mapTypeId: google.maps.MapTypeId.HYBRID
    };
    main_map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

    main_marker = new google.maps.Marker({
        position: myLatlng,
        map: main_map
    });
    main_marker.setDraggable(true);

    google.maps.event.addListener(main_marker, 'dragend', function(event) {
        var markerLatlng = main_marker.getPosition();
        $("#id_latitud").val(markerLatlng.lat().toString());
        $("#id_longitud").val(markerLatlng.lng().toString());
        main_map.setCenter(markerLatlng);

        if(geocoder) {
            geocoder.geocode({'latLng': markerLatlng}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    if (results[1]) {
                        $("#id_direccion").val(results[1].formatted_address);
                        $(".format_ubicacion").val(results[1].formatted_address);
                    }
                }
            });
        }
    });
}

function loadPreviewMap(map_id, latitud, longitud) {
    var myLatlng = new google.maps.LatLng(latitud.replace(",", "."), longitud.replace(",", "."));

    var myOptions = {
        zoom: 14,
        center: myLatlng,
        mapTypeId: google.maps.MapTypeId.HYBRID
    };
    preview_map = new google.maps.Map(document.getElementById(map_id), myOptions);

    preview_marker = new google.maps.Marker({
        position: myLatlng,
        map: preview_map
    });
}

function loadReferencesMap(map_id, latitud, longitud, references) {
    var myLatlng = new google.maps.LatLng(latitud.replace(",", "."), longitud.replace(",", "."));

    var myOptions = {
        zoom: 14,
        center: myLatlng,
        mapTypeId: google.maps.MapTypeId.HYBRID
    };
    references_map = new google.maps.Map(document.getElementById(map_id), myOptions);

    preview_marker = new google.maps.Marker({
        position: myLatlng,
        map: references_map
    });

    var new_marker;
    var array_marker = [];
    var info_window;
    var array_info_window = [];

    for(i = 0; i < references.length; i++) {
        new_marker = new google.maps.Marker({
            position: references[i].latlng,
            map: references_map,
            title: references[i].nombre,
            icon: references[i].icono,
            draggable: false,
            content:
                "<div class='span-5 info_window'>" +
                    "<h1>" + references[i].nombre + "</h1>" +
                    "<p>" + references[i].descripcion + "</p>" +
                "</div>"
        });
        array_marker.push(new_marker);

        info_window = new google.maps.InfoWindow({
            content: ""
        });

        google.maps.event.addListener(new_marker, 'click', function() {
            info_window.setContent(this.content);
            info_window.open(references_map, this);
        });
    }
}

function loadResultsMap(map_id, results, bounds) {
    var myOptions = {
        zoom: 10,
        mapTypeId: google.maps.MapTypeId.HYBRID,
        center: bounds.getCenter()
    }
    result_map = new google.maps.Map(document.getElementById(map_id), myOptions);
    result_map.setCenter(bounds.getCenter());

    var new_marker;
    var array_marker = [];
    var info_window;
    var array_info_window = [];

    for(i = 0; i < results.length; i++) {
        new_marker = new google.maps.Marker({
            position: results[i].latlng,
            map: result_map,
            title: results[i].nombre,
            draggable: false,
            content:
                "<div class='span-5 info_window'>" +
                    "<div class='span-3'>" +
                        "<a href='" + results[i].link + "'>" +
                            "<img src='" + results[i].bigIcon + "' />" +
                        "</a>" +
                    "</div>" +
                    "<div class='span-2 last'>" +
                        "<div class='span-2 last'>" +
                            "<a href='" + results[i].link + "'>" +
                                "<h1>" + results[i].nombre + "</h1>" +
                            "</a>" +
                            "<h2>" + results[i].rubro + "</h2>" +
                        "</div>" +
                        "<div class='span-2 last'>" +
                            "<p>" + results[i].direccion + "</p>" +
                        "</div>" +
                    "</div>" +
                "</div>"
        })
        array_marker.push(new_marker);

        info_window = new google.maps.InfoWindow({
            content: ""
        });

        google.maps.event.addListener(new_marker, 'click', function() {
            info_window.setContent(this.content);
            info_window.open(result_map, this);
        });
    }
}

function loadUbicacionMap() {
    geocoder = new google.maps.Geocoder();

    var myLatlng = new google.maps.LatLng(-16.398748,-71.536961);

    var myOptions = {
        zoom: 8,
        center: myLatlng,
        mapTypeId: google.maps.MapTypeId.HYBRID
    }
    map = new google.maps.Map(document.getElementById("map_ubicacion"), myOptions);

    place_marker = new google.maps.Marker({
        position: myLatlng,
        map: map
    });
    place_marker.setDraggable(true);

    google.maps.event.addListener(place_marker, 'dragend', function(event) {
        var markerLatlng = place_marker.getPosition();
        map.setCenter(markerLatlng);

        if(geocoder) {
            geocoder.geocode({'latLng': markerLatlng}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    if (results[1]) {
                        $("#id_ubicacion").val(results[1].formatted_address);
                        $(".format_ubicacion").val(results[1].formatted_address);
                    }
                }
            });
        }
    });
}