function MapArea(map_id, area, start_marker_pos, end_marker_pos) {
    // Mapa
    var map_options = {
        zoom: 7,
        center: new google.maps.LatLng(-16.161921,-71.575928),
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById(map_id), map_options);

    // Iconos
    var imgVertex = new google.maps.MarkerImage(
        'css/vertex.png',
        new google.maps.Size(11, 11),
        new google.maps.Point(0, 0),
        new google.maps.Point(6, 6)
    );
    var imgVertexOver = new google.maps.MarkerImage(
        'css/vertexOver.png',
        new google.maps.Size(11, 11),
        new google.maps.Point(0, 0),
        new google.maps.Point(6, 6)
    );

    // Marcadores
    var marker_options = {
        //icon: imgVertex,
        map: map,
        draggable: true
    };
    var start_marker = new google.maps.Marker(marker_options);
    var end_marker = new google.maps.Marker(marker_options);
    if(start_marker_pos != undefined && end_marker_pos != undefined) {
        start_marker.setPosition(start_marker_pos);
        end_marker.setPosition(end_marker_pos);
        area.setBounds(new google.maps.LatLngBounds(start_marker_pos, end_marker_pos));
    }

    // Area
    area.setMap(map);

    var stage = 0;

    google.maps.event.addListener(map, 'click', function(event) {
        if(stage == 0) {
            start_marker.setPosition(event.latLng);
            start_marker_pos = event.latLng;
            end_marker.setPosition();
            end_marker_pos = event.latLng;
            area.setBounds();
            stage = 1;
        }
        else {
            end_marker.setPosition(event.latLng);
            end_marker_pos = event.latLng;
            refreshArea();
            stage = 0;
        }
    });

    google.maps.event.addListener(start_marker, 'drag', function(event) {
        refreshArea();
    });

    google.maps.event.addListener(end_marker, 'drag', function(event) {
        refreshArea();
    });

    this.refreshArea = function() {
        if(start_marker.getPosition().lat() < end_marker.getPosition().lat()) {
            var temp = start_marker;
            start_marker = end_marker;
            end_marker = temp;
        }
        if(start_marker.getPosition().lng() < end_marker.getPosition().lng()) {
            area.setBounds(
                new google.maps.LatLngBounds(
                    start_marker.getPosition(),
                    end_marker.getPosition())
            );
        }
        else {
            alert("El marcador colocado al final debe estar a la derecha del inicio, muévalos hasta ver el cuadro negro del área de búsqueda");
        }
    };
}