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


import sys, subprocess, traceback, json
log=[]
def L(*a): s=" ".join(str(x) for x in a); log.append(s)
try:
    subprocess.run([sys.executable,"-m","pip","install","-q","-U","fabric-data-agent-sdk"],check=True)
    from fabric.dataagent.client import FabricDataAgentManagement
    a=FabricDataAgentManagement("NovolexSalesAgent")
    try:
        conf=a._client.get_configuration()
        L("CONFIG:", json.dumps(getattr(conf,"value",conf), default=str)[:4000])
    except Exception as e:
        L("config err", repr(e))
    try:
        L("SETTINGS:", json.dumps(a.get_settings(), default=str)[:1500])
    except Exception as e:
        L("settings err", repr(e))
    try:
        ds=a.get_datasources()
        L("NUM PROD DATASOURCES:", len(ds))
        for d in ds:
            L("DS repr:", repr(d)[:400])
            L("DS dir:", [x for x in dir(d) if not x.startswith("_")])
            for meth in ("get_tables","get_selected_tables","tables","get_configuration"):
                fn=getattr(d,meth,None)
                if callable(fn):
                    try: L(f"DS.{meth}():", json.dumps(fn(), default=str)[:1500])
                    except Exception as e: L(f"DS.{meth} err", repr(e))
                elif fn is not None:
                    L(f"DS.{meth}:", json.dumps(fn, default=str)[:1500])
    except Exception as e:
        L("datasources err", repr(e), traceback.format_exc())
except Exception as e:
    L("FATAL", repr(e), traceback.format_exc())
import notebookutils
notebookutils.fs.put("Files/_agent_diag.txt", "\n".join(log), True)
print("done")

