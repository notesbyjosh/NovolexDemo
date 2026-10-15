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
def L(*a): log.append(" ".join(str(x) for x in a))
try:
    subprocess.run([sys.executable,"-m","pip","install","-q","-U","fabric-data-agent-sdk"],check=True)
    from fabric.dataagent.client import FabricDataAgentManagement
    a=FabricDataAgentManagement("NovolexSalesAgent")
    # operate on staging datasource
    ds=a.get_datasources()[0]
    L("select() signature help:")
    try:
        import inspect
        L("select sig:", str(inspect.signature(ds.select)))
        L("unselect sig:", str(inspect.signature(ds.unselect)))
    except Exception as e: L("sig err", repr(e))
    conf=ds.get_configuration()
    # walk elements: select every table and its children/measures
    def walk(el, path=()):
        eid=el.get("id"); etype=el.get("type"); disp=el.get("display_name")
        p=path+(eid,)
        yield etype, disp, p, el
        for ch in el.get("children",[]) or []:
            yield from walk(ch, p)
    tables=[]; measures=[]; cols=[]
    for el in conf.get("elements",[]):
        for etype,disp,p,e in walk(el):
            if etype=="semantic_model.table": tables.append((disp,p))
            elif etype=="semantic_model.measure": measures.append((disp,p))
            elif etype=="semantic_model.column": cols.append((disp,p))
    L("counts tables",len(tables),"measures",len(measures),"cols",len(cols))
    # try selecting everything via select() with the element path forms
    selected=0
    for disp,p in tables+measures+cols:
        for arg in (list(p), p[-1], disp):
            try:
                ds.select(arg); selected+=1; break
            except Exception:
                continue
    L("select calls ok:", selected)
    # verify
    conf2=ds.get_configuration()
    def count_sel(els):
        n=0
        for el in els:
            for etype,disp,p,e in walk(el):
                if e.get("is_selected"): n+=1
        return n
    L("selected after:", count_sel(conf2.get("elements",[])))
    # publish
    a.publish_staging(); L("published")
except Exception as e:
    L("FATAL", repr(e), traceback.format_exc())
import notebookutils
notebookutils.fs.put("Files/_agent_fix.txt", "\n".join(log), True)
print("done")

