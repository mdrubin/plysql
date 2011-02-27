$(document).ready(function() {

    jQuery.get('graph.xml', function(data) {

         // id of Cytoscape Web container div
         var div_id = "cytoscapeweb";
         
         // IE explorer
         var xml = data.xml;

         // initialization options
         var options = {
             swfPath: "swf/CytoscapeWeb",
             flashInstallerPath: "swf/playerProductInstall"
         };
         
         // initialize cytoscape web
         var vis = new org.cytoscapeweb.Visualization(div_id, options);
         
         // callback when Cytoscape Web has finished drawing
         vis.ready(function() {
         
             // add a listener for when nodes and edges are clicked
             vis.addListener("click", "nodes", function(event) {
                 handle_click(event);
             })
             .addListener("click", "edges", function(event) {
                 handle_click(event);
             });
             
             function handle_click(event) {
                  var target = event.target;
                  
                  clear();
                  print("event.group = " + event.group);
                  for (var i in target.data) {
                     var variable_name = i;
                     var variable_value = target.data[i];
                     print( "event.target.data." + variable_name + " = " + variable_value );
                  }
             }
             
             function clear() {
                 document.getElementById("note").innerHTML = "";
             }
         
             function print(msg) {
                 document.getElementById("note").innerHTML += "<p>" + msg + "</p>";
             }
         });

         // draw options
         var draw_options = {
             // your data goes here
             network: xml,
             // show pan zoom
             panZoomControlVisible: true 
         };
         
         // draw network
         vis.draw(draw_options);
    });

});
