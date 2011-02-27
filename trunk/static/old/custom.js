$(document).ready(function() {
    
    jQuery.get('graph.xml', function(data) {
        // id of Cytoscape Web container div
        var div_id = "cytoscapeweb";

        //IE explorer
        var xml = data.xml;

        // initialization options
        var options = {
            // where you have the Cytoscape Web SWF
            swfPath: "swf/CytoscapeWeb",
            // where you have the Flash installer SWF
            flashInstallerPath: "swf/playerProductInstall"
        };
        
        // init and draw
        var vis = new org.cytoscapeweb.Visualization(div_id, options);
        vis.draw({ network: xml });
    });

});
/*
$(document).ready(function() {
    jQuery.get('graph.xml', function(data) {
      var xml = data;
    });
});
*/