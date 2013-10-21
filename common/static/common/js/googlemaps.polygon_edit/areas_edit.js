function MapAreas(map, areas, counter) {
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

    var marker_options = {
        //icon: imgVertex,
        map: map,
        draggable: true
    };

    var area_count = counter;

    google.maps.event.addListener(map, 'click', function(event) {
        if(areas[area_count].stage == 0) {
            areas[area_count].instance = false;
            areas[area_count].start_marker = new google.maps.Marker(marker_options);
            areas[area_count].end_marker = new google.maps.Marker(marker_options);
            areas[area_count].area = new google.maps.Rectangle({map: map});
            areas[area_count].start_marker.setPosition(event.latLng);
            areas[area_count].end_marker.setPosition();
            areas[area_count].area.setBounds();
            areas[area_count].stage = 1;

            google.maps.event.addListener(areas[area_count].start_marker, 'drag',
                (function(event, area_count) {
                    return function() {
                        refreshArea(area_count);
                        refreshCloseMarker(area_count);
                    }
                })(event, area_count)
            );

            google.maps.event.addListener(areas[area_count].end_marker, 'drag',
                (function(event, area_count) {
                    return function() {
                        refreshArea(area_count);
                        refreshCloseMarker(area_count);
                    }
                })(event, area_count)
            );
        }
        else {
            areas[area_count].end_marker.setPosition(event.latLng);
            refreshArea(area_count);
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
                (function(event, area_count) {
                    return function() {
                        areas[area_count].start_marker.setMap(null);
                        areas[area_count].end_marker.setMap(null);
                        areas[area_count].close_marker.setMap(null);
                        areas[area_count].area.setMap(null);
                        areas[area_count].stage = false;
                    }
                })(event, area_count)
            );

            area_count++;
            areas[area_count] = {stage: 0};
        }
    });

    this.refreshArea = function(counter) {
        if(areas[counter].start_marker.getPosition().lat() < areas[counter].end_marker.getPosition().lat()) {
            var temp = areas[counter].start_marker;
            areas[counter].start_marker = areas[counter].end_marker;
            areas[counter].end_marker = temp;
        }
        if(areas[counter].start_marker.getPosition().lng() < areas[counter].end_marker.getPosition().lng()) {
            areas[counter].area.setBounds(
                new google.maps.LatLngBounds(
                    areas[counter].start_marker.getPosition(),
                    areas[counter].end_marker.getPosition())
            );
        }
        else {
            // TODO: Colocar algún mensaje para hacer saber que el final debe estar a la derecha del inicio siempre
        }
    };

    this.refreshCloseMarker = function(counter) {
        areas[counter].close_marker.setPosition(
            new google.maps.LatLng(
                areas[counter].start_marker.getPosition().lat(),
                areas[counter].end_marker.getPosition().lng()
            )
        );
    }
}