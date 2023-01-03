import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

fetch("stops.json").then(response => response.json()).then(features => {
    var svg = d3.select("#map");

    var projection = d3.geoMercator().fitExtent(
        [[0, 0], [800, 1200]],
        {
            type: "FeatureCollection",
            features: features.map(feature => {
                return {
                    type: "Feature",
                    geometry: {
                        type: "Point",
                        coordinates: feature[1],
                    }
                };
            }),
        }
    );

    svg.selectAll("path")
        .data(features)
        .enter()
        .append("svg:a")
            .attr("xlink:href", d => `/stops/${d[0]}`)
        .append("circle")
            .attr('cx', d => projection(d[1])[0])
            .attr('cy', d => projection(d[1])[1])
            .attr('r', 2);
        // .append("title").text(d => d[0])
        ;

});
