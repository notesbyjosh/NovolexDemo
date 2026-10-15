# Fabric notebook source

# METADATA ********************

# META {
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "d00ef879-8824-4a9b-8cd0-b3d749a39ed1",
# META       "default_lakehouse_name": "Novolex_Sales",
# META       "default_lakehouse_workspace_id": "3181cf49-09a4-415f-a8a4-abb666de50fb",
# META       "known_lakehouses": [
# META         {
# META           "id": "d00ef879-8824-4a9b-8cd0-b3d749a39ed1"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

from pyspark.sql import functions as F
tables = {"DimDate": "DimDate.csv", "DimProduct": "DimProduct.csv", "DimCustomer": "DimCustomer.csv", "DimSalesTerritory": "DimSalesTerritory.csv", "DimSalesperson": "DimSalesperson.csv", "DimPromotion": "DimPromotion.csv", "FactSales": "FactSales.csv", "FactVariance": "FactVariance.csv"}
for tbl, fn in tables.items():
    df = (spark.read.option('header', True).option('inferSchema', True)
          .csv(f'Files/data/{fn}'))
    df.write.mode('overwrite').format('delta').option('overwriteSchema','true').saveAsTable(tbl)
    print(tbl, df.count(), 'rows')
print('DONE')

