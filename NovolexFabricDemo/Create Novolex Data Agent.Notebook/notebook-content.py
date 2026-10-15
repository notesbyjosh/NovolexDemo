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

%pip install -U fabric-data-agent-sdk

# CELL ********************


from fabric.dataagent.client import create_data_agent, FabricDataAgentManagement
WS = "3181cf49-09a4-415f-a8a4-abb666de50fb"; MODEL_ID = "f9c7ae83-38d5-4831-9f7d-685b22b39120"; AGENT_NAME = "NovolexSalesAgent"
INSTR = "You answer questions about Novolex packaging sales using ONLY the certified semantic model 'Novolex Sales (Direct Lake)'.\nRULES:\n- ALWAYS use the certified measures: [Total Sales], [Gross Profit], [Gross Margin %], [Distinct Orders], [Avg Order Value], [Total Quantity], [Sales YoY %], [Sales Fiscal YTD]. NEVER sum or average the raw fact columns (Sales Amount, Gross Profit Base, Order Quantity) directly.\n- 'net sales' / 'sales' / 'revenue' = [Total Sales]; 'gross margin' = [Gross Margin %]; 'orders' = [Distinct Orders]; 'AOV' = [Avg Order Value]; 'units' = [Total Quantity].\n- Break out by Product[Brand], Product[Segment], Customer[Channel], Customer[Customer Name], 'Sales Territory'[Group]/[Region], Date[Fiscal Year] as the question asks.\n- Currency is USD; report at sensible precision (e.g. $6.0B, 34.5%, 96,626 orders).\n- If a question cannot be answered from this model, say so plainly; never invent numbers.\nCONTEXT: 8 brands led by Hilex Poly; 4 end markets (Foodservice, Grocery & Retail, Industrial, Food Processing); mostly US territories; fiscal year starts June 1."

try:
    agent = create_data_agent(data_agent_name=AGENT_NAME)
except Exception as e:
    print("create note:", e); agent = FabricDataAgentManagement(AGENT_NAME)

agent.update_settings(ai_instructions=INSTR)
agent.add_staging_datasource(artifact_name_or_id=MODEL_ID, workspace_id_or_name=WS)

published = False
for m in ("publish_staging", "publish"):
    fn = getattr(agent, m, None)
    if callable(fn):
        try:
            fn(); published = True; print("published via", m); break
        except Exception as e:
            print("publish", m, "err:", e)
print("METHODS:", [x for x in dir(agent) if not x.startswith("_")])
print("PUBLISHED:", published)
print("AGENT DONE")

