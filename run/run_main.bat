@echo off

REM Define variables
set data_mode=dev
set db_root_path=Bird
set start=0
set end=1
set pipeline_nodes=generate_db_schema+extract_col_value+extract_query_noun+column_retrieve_and_other_info+candidate_generate+align_correct+vote+evaluation
set bert_model=all-MiniLM-L6-v2

set AK=your_ak
set engine1=gpt-4o-0513
set engine2=gpt-3.5-turbo-0125
set engine3=gpt-4-turbo
set engine4=claude-3-opus-20240229
set engine5=gemini-1.5-pro-latest
set engine6=finetuned_nl2sql
set engine7=meta-llama/Meta-Llama-3-70B-Instruct
set engine8=finetuned_colsel
set engine9=finetuned_col_filter
set engine10=gpt-3.5-turbo-instruct

set pipeline_setup={
    "generate_db_schema": {
        "engine": "'%engine1%'",
        "bert_model": "%bert_model%",
        "device":"cpu"
    },
    "extract_col_value": {
        "engine": "'%engine1%'",
        "temperature":0.0
    },
    "extract_query_noun": {
        "engine": "'%engine1%'",
        "temperature":0.0
    },
    "column_retrieve_and_other_info": {
        "engine": "'%engine1%'",
        "bert_model": "%bert_model%",
        "device":"cpu",
        "temperature":0.3,
        "top_k":10
    },
    "candidate_generate":{
        "engine": "'%engine1%'",
        "temperature": 0.7,
        "n":21,
        "return_question":"True",
        "single":"False"
    },
    "align_correct":{
        "engine": "'%engine1%'",
        "n":21,
        "bert_model": "%bert_model%",
        "device":"cpu",
        "align_methods":"style_align+function_align+agent_align"
    }
}

python -u src/main.py ^
    --data_mode %data_mode% ^
    --db_root_path %db_root_path% ^
    --pipeline_nodes %pipeline_nodes% ^
    --pipeline_setup "%pipeline_setup%" ^
    --start %start% ^
    --end %end%
