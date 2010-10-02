'''
integer --> in, teger
ValueError: list.remove(x): x not in list
value . value --> value.value
is
case when then else
cast
'''

import sys
import unittest

import ply.lex as lex    
import ply.yacc as yacc    

import plysql_token_rules    
import plysql_grammar_rules
import re

from plysql_classes import banner
from plysql_classes import Node

import plysql_reference

ref = plysql_reference.PlySqlReference()
ref.showReference()

class TestPlySql(unittest.TestCase):
    pass
    def setUp(self):
        self.lexer = lex.lex(module=plysql_token_rules, reflags = re.IGNORECASE)    

    def parseStatement(self,p_statement,p_start='statement'):       
        print p_statement
        print banner('Lexer Results','=')        
        self.lexer.input(p_statement)    
        for tok in self.lexer:    
            print tok.type.rjust(16) + ' : ' + tok.value    
        print banner('Create Parser','=')
        self.parser = yacc.yacc(start=p_start,module=plysql_grammar_rules,outputdir='out')    
        print banner('Parse','=')        
        result = self.parser.parse(p_statement) 
        print result
        if result != None:
            result.debugMsg(result.getSyntaxStructure(),-1)
            result.showDeps()
        
        return result   
    def printStartBanner(self):
        print banner(sys._getframe(1).f_code.co_name,'#')
        
    def compareDependencies(self,p_dependencies,p_refDependencies=''):
        for k, v in p_dependencies.iteritems():
            if v != []:
                self.assertEqual(v,p_refDependencies[k])
        
    def test_statement1(self):
        '''test_statement1'''
        self.printStartBanner()
        statement          = '''
create view XMCARE_STG.STG_PRODUCTIE_AFSPRAKEN_VW
  as
select    'PRODAFSPR' bron
,         a.JAAR_MAAND
,         isnull(kpl.kstpl_code,'-1')             as KOSTENPLAATS
,         isnull(fin.financiering_id,'ONBEKEND')  as financiering_id
,         isnull(i.item_code,'ONBEKEND')          as ITEM_CODE
,         isnull(i.GROEP_ZORGVORM,'ONBEKEND')     as ZORGVORM
,         t.tarief
-- lookup calculaties
,         RealisatieIsAfspraak
,         FactProductie
,         ProductieGroep
,         AfspraakVerekenenMetRealisatieVan
,         CALC_REALISATIE_AANTAL                                                                                                
,         CALC_REALISATIE_EUROS                                                                                                 
,         CALC_AFSPRAAK_AANTAL                                                                                                  
,         CALC_AFSPRAAK_EUROS                                                                                                   
,         CALC_TARIEF
,         BEDBEZETTING_PERC
,         SemiAdditieveMeetwaarde_Tijd
,         CALC_REALISATIE_AANTAL_SAMTIJD
,         CALC_REALISATIE_EUROS_SAMTIJD                                                                                                 
,         CALC_AFSPRAAK_AANTAL_SAMTIJD                                                                                                  
,         CALC_AFSPRAAK_EUROS_SAMTIJD                                                                                                   
,         CALC_TARIEF_SAMTIJD
,         a.AFSPRAAK
,         case
            when CALC_AFSPRAAK_AANTAL   = 'AFSPRAAK_AANTAL'                                 then afspraak
            else NULL
          end as AFSPRAAK_AANTAL
,         case
            when CALC_AFSPRAAK_EUROS    = 'AFSPRAAK_AANTAL X TARIEF'                        then afspraak * tarief
            when CALC_AFSPRAAK_EUROS    = 'AFSPRAAK_AANTAL X TARIEF_PER_MAAND'              then afspraak * (tarief/12)
            else NULL
          end as AFSPRAAK_EUROS
,         case
            when CALC_AFSPRAAK_AANTAL_SAMTIJD   = 'AFSPRAAK_AANTAL'                         then afspraak 
            else NULL
          end as AFSPRAAK_AANTAL_SAMTIJD
from      XMCARE_IMP.IMP_PRODAFSPR       a
-- lookup van de murale met afspraak item code om zo de financieringsvorm te kunnen bepalen.
left join XMCARE_STG.STG_productie_items i
on        a.rapportage_item = i.item_code
-- lookup van de financiering mbv afspraak financier en murale
left join XMCARE_IMP.IMP_GROEP_FINANCIERINGSVORMEN     fin
on        a.financiering =  fin.financiering
and       (fin.murale is null or i.murale   =  fin.murale)
-- lookup van de tarieven (tarief wordt uniek geidentificeerd door item_code, jaar en financiering)
left join xmcare_stg.stg_productie_tarieven as t
on        a.rapportage_item                   = t.item_code
and       convert(integer,left(JAAR_MAAND,4)) = t.jaar      
and       i.financiering_id                   = t.financiering_id
-- lookup van de kostenplaats (in het geval van een onbekende kostenplaats wil je een -1)
left join inforay_dwh.dbo.axi_cat_kostenplaatsstructuur  kpl
on        a.kostenplaats = kpl.kstpl_code
'''
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)

    def test_statement2(self):
        '''test_statement2'''
        self.printStartBanner()
        statement          = '''
create view [XMCARE_STG].[STG_PRODUCTIE_REALISATIE_VW]
as 
select    *
,         case
            when CALC_REALISATIE_AANTAL         = 'REALISATIE_AANTAL'                     then aantal
            else NULL
          end as REALISATIE_AANTAL
,         case
            when CALC_REALISATIE_EUROS          = 'REALISATIE_AANTAL X TARIEF'            then aantal * tarief
            when CALC_REALISATIE_EUROS          = 'REALISATIE_AANTAL X TARIEF_PER_MAAND'  then aantal * (12.0/52.0) * tarief/12
            when CALC_REALISATIE_EUROS          = 'AFSPRAAK_AANTAL X TARIEF_PER_MAAND'    then afspraak * tarief/12
            when CALC_REALISATIE_EUROS          = 'AFSPRAAK_AANTAL X TARIEF'              then afspraak * tarief
            else NULL
          end as REALISATIE_EUROS
,         case
            when CALC_REALISATIE_AANTAL_SAMTIJD = 'UREN_OPENSTEL_GEM_PER_WK_VANAF_JAN'    then RealisatieGemiddeldOverLopendeJaar * (12.0/52.0)  -- .0 omdat SQL Server het getal interpreteert als integer en er dan 0 als uitkomst komt vreemd genoeg.
            when CALC_REALISATIE_AANTAL_SAMTIJD = 'GEM_BB_PER_DAG_MET_BB_PERC_CORRECTIE'  then RealisatieGemiddeldOverLopendeJaar / (BEDBEZETTING_PERC / 100.0) / (day(dateadd(mm,datediff(mm,-1,cast( MAAND_VERANTWOORDING as varchar(6)) + '01'),-1)))
            when CALC_REALISATIE_AANTAL_SAMTIJD = 'AFSPRAAK_AANTAL'                       then afspraak
            else NULL
          end as REALISATIE_AANTAL_SAMTIJD
,         (day(dateadd(mm,datediff(mm,-1,cast( MAAND_VERANTWOORDING as varchar(6)) + '01'),-1))) dagen_in_maand
from (select    prd.BRON                                                               
      ,         prd.NR_RUN                                                                     
      ,         prd.BOEK_PER                                                                                                               
      ,         prd.PROD_PER                                                                                                               
      ,         convert(varchar(1024),isnull(kpl.kstpl_code,-1)) as KOSTENPLAATS           
      ,         prd.C_CATEGORIE                                                                   
      ,         prd.C_PROJECT                                                                                                              
      ,         prd.OPN1                                                                                                                   
      ,         prd.C_BETAAL_INSTANTIE                                                                                                     
      ,         prd.AANTAL                                                                                                                 
      ,         prd.AFSPRAAK                                                                   
      ,         prd.RealisatieCummulatiefOverLopendeJaar                                       
      ,         prd.RealisatieGemiddeldOverLopendeJaar                                         
      ,         prd.BEDRAG                                                                                             
      ,         prd.FINANCIERING                                                               
      ,         prd.MAAND_VERANTWOORDING                                                       
      ,         prd.ITEM_CODE                                                                  
      ,         prd.ZORGVORM                                                                   
      ,         prd.RealisatieIsAfspraak                                                       
      ,         prd.FactProductie                                                              
      ,         prd.ProductieGroep
      ,         prd.CALC_REALISATIE_AANTAL                                                     
      ,         prd.CALC_REALISATIE_EUROS                                                                                                                       
      ,         prd.CALC_AFSPRAAK_AANTAL                                                                                                                        
      ,         prd.CALC_AFSPRAAK_EUROS                                                                                                                         
      ,         prd.CALC_TARIEF                                                                                                                                 
      ,         prd.BEDBEZETTING_PERC                                                          
      ,         prd.SemiAdditieveMeetwaarde_Tijd                                               
      ,         prd.CALC_REALISATIE_AANTAL_SAMTIJD                                             
      ,         prd.CALC_REALISATIE_EUROS_SAMTIJD                                                                                                                       
      ,         prd.CALC_AFSPRAAK_AANTAL_SAMTIJD                                                                                                                        
      ,         prd.CALC_AFSPRAAK_EUROS_SAMTIJD                                                                                                                         
      ,         prd.CALC_TARIEF_SAMTIJD
      ,         fin.financiering_id  
      ,         tar.tarief  
      from      (select    [BRON]       
                 ,         [NR_RUN]                                                                                                      
                 ,         [BOEK_PER]                                                                                                    
                 ,         [PROD_PER]     
                 -- -1 is key voor onbekend record. Converteer kostenplaats naar string om conversieproblemen te voorkomen.   
                 ,         convert(varchar(1024),isnull([KOSTENPLAATS],-1)) as [KOSTENPLAATS]   
                 ,         [C_CATEGORIE]                                                                                                 
                 ,         [C_PROJECT]                                                                                                   
                 ,         [OPN1]                                                                                                        
                 ,         [C_BETAAL_INSTANTIE]                                                                                          
                 ,         [AANTAL]   
                 ,         null as [AFSPRAAK]          
                 ,         RealisatieCummulatiefOverLopendeJaar  
                 ,         RealisatieGemiddeldOverLopendeJaar                                                      
                 ,         [BEDRAG]   
                 -- bepaling van financiering volgens definitie                                                                          
                 ,         case                                                                                                          
                             when c_betaal_instantie is null         then isnull(groep_financiering,'ONBEKEND')  
                             when c_betaal_instantie = 'FPZ'         then 'FPZ'                                                          
                             when c_betaal_instantie = 'RW-WISSEL'   then 'ROOIJSEWISSEL'                                                
                             when c_betaal_instantie = 'ZRADELFT'    then 'ZRA'                                                          
                             when c_betaal_instantie = 'ZORGKANT'    then isnull(groep_financiering,'ONBEKEND')  
                             else                                           'OVERIGE'                                                    
                           end as FINANCIERING         
                 -- bepaling van verantwoordingsperiode volgens definitie                                                                
                 ,         case                                                                                                          
                             when groep_financiering = 'ZVW'   
                               then BOEK_PER                                                                           
                             else   PROD_PER                                                                           
                           end                                                  as MAAND_VERANTWOORDING     
                 -- lookup item attributen 
                 ,         isnull(i.item_code,'ONBEKEND')            as ITEM_CODE  
                 ,         isnull(i.groep_zorgvorm,'ONBEKEND')       as ZORGVORM
                 ,         i.RealisatieIsAfspraak
                 ,         i.FactProductie
                 ,         i.ProductieGroep
                 ,         i.CALC_REALISATIE_AANTAL                                                                                                           
                 ,         i.CALC_REALISATIE_EUROS                                                                                                            
                 ,         i.CALC_AFSPRAAK_AANTAL                                                                                                             
                 ,         i.CALC_AFSPRAAK_EUROS                                                                                                              
                 ,         i.CALC_TARIEF           
                 ,         i.BEDBEZETTING_PERC
                 ,         i.SemiAdditieveMeetwaarde_Tijd
                 ,         i.CALC_REALISATIE_AANTAL_SAMTIJD                                                                                                           
                 ,         i.CALC_REALISATIE_EUROS_SAMTIJD                                                                                                            
                 ,         i.CALC_AFSPRAAK_AANTAL_SAMTIJD                                                                                                             
                 ,         i.CALC_AFSPRAAK_EUROS_SAMTIJD                                                                                                              
                 ,         i.CALC_TARIEF_SAMTIJD           
                 from      XMCARE_STG.STG_PRODUCTIE_REALISATIE_SRC                                p
                 -- lookup van de item attributen mbv. item_code  
                 join      XMCARE_STG.STG_PRODUCTIE_ITEMS                                         i  -- geen left join omdat er anders allemaal onbekende items/financiers etc. in de rapportage komen.
                 on        p.item_code    =  i.item_code                        
                )                                                                                 prd             
      -- lookup van de financiering mbv. murale. lookup via UK, wordt automatisch getest  
      left join XMCARE_IMP.IMP_GROEP_ZORGVORMEN                                                   zvm  
      on        prd.zorgvorm     =  zvm.zorgvorm                        
      -- lookup via UK, wordt automatisch getest  
      left join XMCARE_IMP.IMP_GROEP_FINANCIERINGSVORMEN                                          fin  
      on        prd.financiering =  fin.financiering                    
      and       (fin.murale is null or zvm.murale      =  fin.murale)  
      -- lookup van de tarieven via UK item_code, jaar en financiering, wordt automatisch getest  
      left join xmcare_stg.stg_productie_tarieven as                                              tar  
      on        prd.item_code                                 = tar.item_code  
      and       convert(integer,left(MAAND_VERANTWOORDING,4)) = tar.jaar        
      and       fin.financiering_id                           = tar.financiering_id  
      -- lookup van de kostenplaats (in het geval van een onbekende kostenplaats wil je een -1)
      left join inforay_dwh.dbo.axi_cat_kostenplaatsstructuur  kpl
      on        prd.kostenplaats = kpl.kstpl_code
        union ALL
      SELECT [bron]
      ,-1            rn
      ,[JAAR_MAAND]  jm1
      ,[JAAR_MAAND]  jm2
      ,[KOSTENPLAATS]
      ,cast(null as varchar(1024)) 
      ,cast(null as varchar(1024)) 
      ,cast(null as varchar(1024)) 
      ,cast(null as varchar(1024)) 
      ,cast(null as float)         
      ,AFSPRAAK
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as varchar(1024)) 
      ,[JAAR_MAAND]
      ,[ITEM_CODE]
      ,[ZORGVORM]
      ,[RealisatieIsAfspraak]
      ,[FactProductie]
      ,[ProductieGroep]
      ,[CALC_REALISATIE_AANTAL]
      ,[CALC_REALISATIE_EUROS]
      ,[CALC_AFSPRAAK_AANTAL]
      ,[CALC_AFSPRAAK_EUROS]
      ,[CALC_TARIEF]
      ,[BEDBEZETTING_PERC]
      ,[SemiAdditieveMeetwaarde_Tijd]
      ,[CALC_REALISATIE_AANTAL_SAMTIJD]
      ,[CALC_REALISATIE_EUROS_SAMTIJD]
      ,[CALC_AFSPRAAK_AANTAL_SAMTIJD]
      ,[CALC_AFSPRAAK_EUROS_SAMTIJD]
      ,[CALC_TARIEF_SAMTIJD]
      ,[financiering_id]
      ,[tarief]
      FROM [XMCARE_SRC].[XMCARE_STG].[STG_PRODUCTIE_AFSPRAKEN]
      WHERE [RealisatieIsAfspraak] = 1
        union ALL
      SELECT         [BRON]
      ,-1            [NR_RUN]
      ,[JAAR_MAAND]  [BOEK_PER]
      ,[JAAR_MAAND]  [PROD_PER]
      ,[KOSTENPLAATS]
      ,cast(null as varchar(1024))  [C_CATEGORIE]
      ,cast(null as varchar(1024))  [C_PROJECT]
      ,cast(null as varchar(1024))  [OPN1]
      ,cast(null as varchar(1024))  [C_BETAAL_INSTANTIE]
      ,AFSPRAAK                     [AANTAL] 
      ,cast(null as float)          [AFSPRAAK]
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as varchar(1024)) 
      ,[JAAR_MAAND]
      ,[ITEM_CODE]
      ,[ZORGVORM]
      ,[RealisatieIsAfspraak]
      ,[FactProductie]
      ,[ProductieGroep]
      ,[CALC_REALISATIE_AANTAL]
      ,[CALC_REALISATIE_EUROS]
      ,[CALC_AFSPRAAK_AANTAL]
      ,[CALC_AFSPRAAK_EUROS]
      ,[CALC_TARIEF]
      ,[BEDBEZETTING_PERC]
      ,[SemiAdditieveMeetwaarde_Tijd]
      ,[CALC_REALISATIE_AANTAL_SAMTIJD]
      ,[CALC_REALISATIE_EUROS_SAMTIJD]
      ,[CALC_AFSPRAAK_AANTAL_SAMTIJD]
      ,[CALC_AFSPRAAK_EUROS_SAMTIJD]
      ,[CALC_TARIEF_SAMTIJD]
      ,[financiering_id]
      ,[tarief]
      FROM [XMCARE_SRC].[XMCARE_STG].[STG_PRODUCTIE_AFSPRAKEN]
      WHERE [AfspraakVerekenenMetRealisatieVan] is not null
        union ALL
      SELECT         [BRON]
      ,-1            [NR_RUN]
      ,[JAAR_MAAND]  [BOEK_PER]
      ,[JAAR_MAAND]  [PROD_PER]
      ,[KOSTENPLAATS]
      ,cast(null as varchar(1024))  [C_CATEGORIE]
      ,cast(null as varchar(1024))  [C_PROJECT]
      ,cast(null as varchar(1024))  [OPN1]
      ,cast(null as varchar(1024))  [C_BETAAL_INSTANTIE]
      ,-AFSPRAAK                     [AANTAL]             -- negatieve afspraak
      ,cast(null as float)          [AFSPRAAK]
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as varchar(1024)) 
      ,[JAAR_MAAND]
      ,[ITEM_CODE]
      ,[ZORGVORM]
      ,[RealisatieIsAfspraak]
      ,[FactProductie]
      ,[ProductieGroep]
      ,[CALC_REALISATIE_AANTAL]
      ,[CALC_REALISATIE_EUROS]
      ,[CALC_AFSPRAAK_AANTAL]
      ,[CALC_AFSPRAAK_EUROS]
      ,[CALC_TARIEF]
      ,[BEDBEZETTING_PERC]
      ,[SemiAdditieveMeetwaarde_Tijd]
      ,[CALC_REALISATIE_AANTAL_SAMTIJD]
      ,[CALC_REALISATIE_EUROS_SAMTIJD]
      ,[CALC_AFSPRAAK_AANTAL_SAMTIJD]
      ,[CALC_AFSPRAAK_EUROS_SAMTIJD]
      ,[CALC_TARIEF_SAMTIJD]
      ,[AfspraakVerekenenMetRealisatieVan]  -- verrekenen met financier
      ,[tarief]
      FROM [XMCARE_SRC].[XMCARE_STG].[STG_PRODUCTIE_AFSPRAKEN]
      WHERE [AfspraakVerekenenMetRealisatieVan] is not null
      ) q
'''
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)

def tearDown(self):
        self.lexer = None
        self.parser = None
        
unittest.main()
