pageHeader='''
              <p align="left"> 
                <a href="/">Home</a> &nbsp; 
                <a href="what-is-plysql">What is PlySql ?</a> &nbsp; 
                <a href="http://code.google.com/p/plysql/">Project Home</a> &nbsp; 
                <a href="http://blog.holkevisser.nl/">My Blog</a> &nbsp; 
              </p> 
              <!-- Parse | Metadata | SqlDoc | Sqetl -->
              <hr>
           '''

formButton='''<button type="submit" > <div style="font-size:24px"> Get Sql Metadata </div> </button>'''

htmlHead='''
  <head>    
    <title>PlySql: Query metadata analyzer</title>     
    <script type="text/javascript">    
        
      var _gaq = _gaq || [];    
      _gaq.push(['_setAccount', 'UA-3437426-3']);    
      _gaq.push(['_trackPageview']);    
        
      (function() {    
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;    
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';    
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);    
      })();    
        
    </script>    
  </head>    
'''

pageFooter='''
      <p><a href="http://blog.holkevisser.nl/">My Blog</a> &nbsp; <a href="http://code.google.com/p/plysql/">Project Home</a></p>
      <p>Plysql is under development. </p>
      <p>Plysql is a python application that can do a metadata-analysis on sql queries and scripts in Micorsoft Sql Server and Oracle syntax.</p>
      <p>At this moment only create view, create table and select statements are supported.</p>
      <p>The metadata can be usefull in etl, sql formating and documenting tools or it can be used to perform lineage and impact analysis. </p>

'''