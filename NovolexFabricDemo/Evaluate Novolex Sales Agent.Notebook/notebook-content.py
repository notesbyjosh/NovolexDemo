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

# MARKDOWN ********************

# # Evaluate the Novolex Sales Data Agent
# 
# Grades the **NovolexSalesAgent** against a ground-truth answer key drawn from the certified
# **Novolex Sales (Direct Lake)** model. Uses `fabric.dataagent.evaluation`.
# 
# > Synthetic data. Ground truth: **$5.97B** net sales, **34.5%** gross margin, **96,626** orders,
# > lead brand **Hilex Poly (~$1.8B)**.


# CELL ********************

%pip install -U fabric-data-agent-sdk

# CELL ********************

import pandas as pd

df = pd.DataFrame(
    columns=["question", "expected_answer"],
    data=[
        ["What were our total net sales?", "$5.97 billion (about $5,967,081,550)"],
        ["Which brand had the highest net sales?", "Hilex Poly, at about $1.8 billion"],
        ["What is our overall gross margin percentage?", "About 34.5%"],
        ["Which region had the highest net sales?", "North America, at about $4.25 billion"],
        ["Which product segment is the largest by net sales?", "Foodservice, at about $3.15 billion"],
        ["How many orders did we have?", "96,626 orders"],
        ["What was our average order value?", "About $61,754"],
        ["Which sales channel drove the most net sales?", "Foodservice Distributor, at about $1.58 billion"],
    ],
)
df

# CELL ********************

from fabric.dataagent.evaluation import evaluate_data_agent

data_agent_name = "NovolexSalesAgent"   # exact item name in NovolexDemo
workspace_name = None                    # None = current workspace (NovolexDemo)
table_name = "novolex_eval_output"       # summary + novolex_eval_output_steps
data_agent_stage = "production"          # the published stage

try:
    evaluation_id = evaluate_data_agent(
        df, data_agent_name, workspace_name=workspace_name,
        table_name=table_name, data_agent_stage=data_agent_stage,
    )
    print(f"Evaluation run ID: {evaluation_id}")
except Exception as e:
    print(f"Evaluation failed: {e}")

# CELL ********************

from fabric.dataagent.evaluation import get_evaluation_summary
get_evaluation_summary(table_name)

# CELL ********************

from fabric.dataagent.evaluation import get_evaluation_details
get_evaluation_details(evaluation_id, table_name, get_all_rows=True, verbose=True)

# MARKDOWN ********************

# ## Strict critic
# Grades a row correct only when the key figure (within ~1%) **and** the named entity match.

# CELL ********************

critic_prompt = """
You are grading a sales analytics answer for Novolex.
Mark 'yes' ONLY if the actual answer conveys the same key figure (within ~1% rounding)
AND the same named entity (brand / region / segment / channel) as the expected answer.
Ignore differences in wording, currency formatting, or extra commentary.

Query: {query}
Expected Answer: {expected_answer}
Actual Answer: {actual_answer}

Is the actual answer equivalent to the expected answer? Respond 'yes' or 'no'.
"""

evaluation_id_strict = evaluate_data_agent(
    df, data_agent_name, table_name="novolex_eval_strict",
    data_agent_stage=data_agent_stage, critic_prompt=critic_prompt,
)
print(f"Strict evaluation run ID: {evaluation_id_strict}")
get_evaluation_summary("novolex_eval_strict")

# MARKDOWN ********************

# ## Catch a failure
# One row is deliberately wrong (Vegware is **not** the top brand). The critic should flag it.

# CELL ********************

df_trap = pd.DataFrame(
    columns=["question", "expected_answer"],
    data=[
        ["What were our total net sales?", "$5.97 billion (about $5,967,081,550)"],
        ["Which brand had the highest net sales?", "Hilex Poly, at about $1.8 billion"],
        # WRONG on purpose — the true top brand is Hilex Poly, NOT Vegware.
        ["Which brand had the highest net sales?", "Vegware, at about $4.9 billion"],
    ],
)

evaluation_id_trap = evaluate_data_agent(
    df_trap, data_agent_name, table_name="novolex_eval_trap", data_agent_stage=data_agent_stage,
)
print(f"Catch-a-failure run ID: {evaluation_id_trap}")
display(get_evaluation_summary("novolex_eval_trap"))
get_evaluation_details(evaluation_id_trap, "novolex_eval_trap", get_all_rows=False, verbose=True)
