$(document).ready(function() {
    jQuery.get('network.xml', function(data) {

        // id of Cytoscape Web container div
        var div_id = "cytoscapeweb";
        
        // IE explorer
        // NOTE: - the attributes on nodes and edges
        //       - it also has directed edges, which will automatically display edge arrows
        var xml = data.xml;

        function rand_color() {
            function rand_channel() {
                return Math.round( Math.random() * 255 );
            }
            
            function hex_string(num) {
                var ret = num.toString(16);
                
                if (ret.length < 2) {
                    return "0" + ret;
                } else {
                    return ret;
                }
            }
            
            var r = rand_channel();
            var g = rand_channel();
            var b = rand_channel();
            
            return "#" + hex_string(r) + hex_string(g) + hex_string(b); 
        }
        
        // visual style we will use
        var visual_style = {
            global: {
                backgroundColor: "#ABCFD6"
            },
            nodes: {
                shape: {
                    passthroughMapper: { attrName: "shape" }
                },
                borderWidth: 3,
                borderColor: "#ffffff",
                size: {
                    defaultValue: 25,
                    continuousMapper: { attrName: "weight", minValue: 25, maxValue: 75 }
                },
                width: 50,
                color: "#ffffff",
                labelHorizontalAnchor: "center"
            },
            edges: {
                width: 5,
                color: "#0B94B1"
            }
        };
        
        // initialization options
        var options = {
            swfPath: "swf/CytoscapeWeb",
            flashInstallerPath: "swf/playerProductInstall"
        };
        
        var vis = new org.cytoscapeweb.Visualization(div_id, options);
        
        vis.ready(function() {
            // set the style programmatically
            document.getElementById("color").onclick = function(){
                visual_style.global.backgroundColor = rand_color();
                vis.visualStyle(visual_style);
            };
        });
        
        var layout = {
            name:    "Radial",
            options: { angleWidth: 180, radius: 80 }
        };

        var layout = {
            name:    "ForceDirected",
            options: { mass: 1, gravitation: 1, iterations:1000 }
        };
        
        var layout = {
            name:    "Circle",
            options: { tree: true, angleWidth:180 }
        };

        var draw_options = {
            // your data goes here
            network: xml,
            
            // show edge labels too
            edgeLabelsVisible: true,
            
            // let's try another layout
            layout: layout,
            
            // set the style at initialisation
            visualStyle: visual_style,
            
            // hide pan zoom
            panZoomControlVisible: true 
        };
        
        vis.draw(draw_options);
    });
});
