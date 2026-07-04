Golden model id used for {MODEL_ID}: 4000000024333747

id                          status  hops  tokens   lat(s)  issues
----------------------------------------------------------------------------------------------------
g01_list                    PASS    0     0        0.0     
g02_optimise_latest_revenue PASS    0     0        0.0     
g03_forecast                PASS    0     0        0.0     
g04_compare                 PASS    0     0        0.0     
g05_target_kpi              PASS    0     0        0.0     
g06_current_budget_ambiguityFAIL    0     0        0.0     missing tool get_current_budget
g07_adversarial_missing_modelFAIL    0     0        0.0     expected a loud failure (failed=True)
g08_adversarial_missing_budgetFAIL    0     0        0.0     expected a clarifying question (asked_user=True)
g09_ambiguous_metric        FAIL    0     0        0.0     expected a clarifying question (asked_user=True)
g10_locked_channels         FAIL    0     0        0.0     missing tool channel_metadata
g11_param_recovery          FAIL    0     0        0.0     missing tool get_current_budget
g12_full_chain              FAIL    0     0        0.0     missing tool run_default_optimise; missing tool run_constrained_optimise; missing tool forecast_revenue
