import inspect
import unittest

import plysql_unittests
import plysql_reference

#ref = plysql_reference.PlySqlReference()
#ref.showReference()

# Run 1
#unittest.main()

# Run 2.1
#suite = plysql_unittests.TestPlySql().suite()
#unittest.TextTestRunner(verbosity=2).run(suite)

# Run 2.2
#suite = unittest.TestLoader().loadTestsFromTestCase(plysql_unittests.TestPlySql)
#unittest.TextTestRunner(verbosity=2).run(suite)

# Run 2.3
#suite = unittest.TestSuite()
#suite.addTest(plysql_unittests.TestPlySql('test_9'))
#unittest.TextTestRunner(verbosity=2).run(suite)

# Run 2.4
# tests = ['test_subquery_2']
# suite = unittest.TestSuite( [plysql_unittests.TestPlySql(t) for t in tests] )
# unittest.TextTestRunner(verbosity=2).run(suite)

###########################################################
#suite = unittest.TestLoader().loadTestsFromTestCase(plysql_unittests.TestPlySql)

# test create table
tests = [
'test_1',
'test_2',
'test_3',
'test_5',
'test_6',
'test_7',
'test_8',
'test_9',
'test_alias_1',
'test_alias_2',
#'test_alias_3',         # subquery
'test_and_or_1',
'test_case_2',
'test_case_alias',
'test_cast_1',
'test_cast_2',
'test_create_table_1',
'test_create_table_2',
'test_function_1',
'test_function_2',
'test_is_null',
'test_join_1',
'test_partition_by_1',
'test_partition_by_2',
'test_reserved_words',
'test_star_dot_1',
'test_star_dot_2_alias',
'test_star_dot_3',
'test_star_dot_4_alias',
'test_star_dot_5',
'test_star_dot_6',
'test_statement1',
'test_statement2',
'test_statement3',
#'test_subquery_4',
#'test_subquery_1',      
#'test_subquery_2',
#'test_subquery_3',
#'test_view_1'           
]

tests=['test_between_01']

# Run all
#suite = unittest.TestLoader().loadTestsFromTestCase(plysql_unittests.TestPlySql)

# Run tests
suite = unittest.TestSuite( [plysql_unittests.TestPlySql(t) for t in tests] )
unittest.TextTestRunner(verbosity=2).run(suite)

'''
# get test functions
m=inspect.getmembers(plysql_unittests.TestPlySql)
l=[]
for name,type in m:
    if name[0:4] == 'test' :
        l += [name]
print l
'''
