import plysql_web

print'''
<html>
<head>
</head>
<body>
    '''

print plysql_web.pageHeader

print '''
<p>Plysql is under development. </p>
<p>Plysql is a python application that can do a metadata-analysis on sql queries and scripts. </p>
<p>The metadata could be usefull in etl, sql formating and documenting tools or it can be used to perform lineage and impact analysis. </p>
<p>PlySql can parse sql statements in Micorsoft Sql Server and Oracle syntax.</p>
</body>
</html>
'''
