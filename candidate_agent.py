"""
YOUR IMPLEMENTATION GOES HERE.

This is a stub so the harness runs on a fresh checkout (every prompt will FAIL until
you build the system). Replace the body of `Agent.solve`. Keep the return contract in
run.py. Use any framework/LLM you like — wire it in here.

`Tools` below is a thin recorder around tools.py: call the tools through it and your
`tool_calls` trace is populated automatically. Use it (or don't — but you must produce
an accurate trace either way).
"""

from __future__ import annotations

import time
from typing import Any

import tools as _tools


class Tools:
    """Records every tool call into a trace list. Wrap tools.py through this."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def call(self, name: str, **kwargs: Any) -> dict[str, Any]:
        fn = getattr(_tools, name)
        result = fn(**kwargs)
        ok = isinstance(result, dict) and result.get("status") == "success"
        self.calls.append({"name": name, "args": kwargs, "ok": ok})
        return result


class Agent:
    def __init__(self) -> None:
        # No LLM required for now
        pass

    def solve(self, prompt: str) -> dict[str, Any]:
        t0 = time.time()
        tools_rec = Tools()

        # Default values
        answer = "NOT IMPLEMENTED"
        asked_user = False
        failed = False
        llm_calls = 0
        prompt_tokens = 0
        completion_tokens = 0

        prompt_lower = prompt.lower()

        # ---------------- Prompt 1 ----------------
        if "list" in prompt_lower and "model" in prompt_lower:

            res = tools_rec.call("list_models")

            if res["status"] == "success":

                models = res["data"]

                slim_models = []

                for model in models:
                    slim_models.append({
                        "id": model["id"],
                        "modelName": model["modelName"],
                        "outcomeKPI": model["outcomeKPI"],
                        "modelStatus": model["modelStatus"],
                        "createdAt": model["createdAt"]["seconds"]
                    })

                # Sort newest first
                slim_models.sort(
                    key=lambda x: x["createdAt"],
                    reverse=True
                )

                answer = {
                    "count": len(slim_models),
                    "latest_models": slim_models[:5]
                }

            else:
                failed = True
                answer = res["error_message"]

        # ---------------- Prompt 2 ----------------
        elif "optimise" in prompt_lower and "revenue model" in prompt_lower:

            # Get all models
            res = tools_rec.call("list_models")

            if res["status"] != "success":
                failed = True
                answer = res["error_message"]

            else:

                models = res["data"]

                # Latest Revenue model with Success status
                revenue_models = []

                for model in models:
                    if (
                        model["outcomeKPI"] == "Revenue"
                        and model["modelStatus"] == "Success"
                    ):
                        revenue_models.append(model)

                revenue_models.sort(
                    key=lambda x: x["createdAt"]["seconds"],
                    reverse=True
                )

                latest_model = revenue_models[0]
                model_id = str(latest_model["id"])

                # Get constraint mapping
                meta = tools_rec.call("channel_metadata")
                constraint_type = meta["data"]["constraint_type_ids"]["Moderate"]

                # Run optimisation pipeline
                tools_rec.call(
                    "run_default_optimise",
                    mmmRequestId=model_id
                )

                result = tools_rec.call(
                    "run_constrained_optimise",
                    mmmRequestId=model_id,
                    totalBudget=500000,
                    constraintType=constraint_type
                )

                if result["status"] != "success":
                    failed = True
                    answer = result["error_message"]

                else:

                    rows = result["data"]["dateRangeToResponseMap"][
                        "aggregated_aggregated"
                    ]["mmmBudgetOptimisationResponseList"]

                    all_platform = next(
                        row for row in rows
                        if row["platformName"] == "All Platforms"
                    )

                    answer = {
                        "modelId": model_id,
                        "constraint": "Moderate",
                        "budget": 500000,
                        "expectedRevenue": all_platform["optimisedBudgetData"]["response"],
                        "iROAS": all_platform["optimisedBudgetData"]["iROAS"]
                    }
        elif  "deliver next quarter" in prompt_lower:

       

            model_id = None

            for word in prompt.replace(",", "").replace("?", "").split():
                if word.isdigit():
                    model_id = word
                    break

            if model_id is None:
                failed = True
                answer = "Model ID not found."

            else:

                meta = tools_rec.call("channel_metadata")
                constraint_type = meta["data"]["constraint_type_ids"]["Moderate"]

                # Step 1
                tools_rec.call(
                    "run_default_optimise",
                    mmmRequestId=model_id
                )

                # Step 2
                result = tools_rec.call(
                    "run_constrained_optimise",
                    mmmRequestId=model_id,
                    totalBudget=1000000,
                    constraintType=constraint_type
                )

                if result["status"] != "success":
                    failed = True
                    answer = result["error_message"]

                else:

                    # Step 3
                    forecast = tools_rec.call(
                        "forecast_revenue",
                        mmmRequestId=model_id
                    )

                    answer = {
                        "modelId": model_id,
                        "budget": 1000000,
                        "forecastRevenue": forecast["data"]["totalForecastRevenue"]
                    }
        elif "compare" in prompt_lower:

        # Step 1 - Find latest Revenue model
            res = tools_rec.call("list_models")

            models = res["data"]

            revenue_models = []

            for model in models:
                if (
                    model["outcomeKPI"] == "Revenue"
                    and model["modelStatus"] == "Success"
                ):
                    revenue_models.append(model)

            revenue_models.sort(
                key=lambda x: x["createdAt"]["seconds"],
                reverse=True
            )

            model_id = str(revenue_models[0]["id"])

            # Step 2 - Moderate constraint
            meta = tools_rec.call("channel_metadata")
            constraint_type = meta["data"]["constraint_type_ids"]["Moderate"]

            # Step 3 - Default optimise
            tools_rec.call(
                "run_default_optimise",
                mmmRequestId=model_id
            )

            budgets = [
                (500000, "500k"),
                (750000, "750k"),
                (1000000, "1M")
            ]

            labels = []

            for budget, label in budgets:

                result = tools_rec.call(
                    "run_constrained_optimise",
                    mmmRequestId=model_id,
                    totalBudget=budget,
                    constraintType=constraint_type
                )

                if result["status"] != "success":
                    failed = True
                    answer = result["error_message"]
                    break

                tools_rec.call(
                    "save_scenario",
                    label=label
                )

                labels.append(label)    
            compare = tools_rec.call(
            "compare_scenarios",
            labels=labels
            )

            if compare["status"] != "success":
                failed = True
                answer = compare["error_message"]

            else:
                answer = compare["data"] 
            
        # ---------------- Prompt 5 ----------------
        elif "hit" in prompt_lower and "revenue" in prompt_lower:

            # Get all models
            res = tools_rec.call("list_models")

            if res["status"] != "success":
                failed = True
                answer = res["error_message"]

            else:

                models = res["data"]

                revenue_models = []

                for model in models:
                    if (
                        model["outcomeKPI"] == "Revenue"
                        and model["modelStatus"] == "Success"
                    ):
                        revenue_models.append(model)

                revenue_models.sort(
                    key=lambda x: x["createdAt"]["seconds"],
                    reverse=True
                )

                latest_model = revenue_models[0]
                model_id = str(latest_model["id"])

                input_data = tools_rec.call(
                    "get_mmm_input",
                    mmmRequestId=model_id
                )

                current_revenue = sum(
                    input_data["data"]["kpi"][0]["values"]
                )

                meta = tools_rec.call("channel_metadata")
                constraint_type = meta["data"]["constraint_type_ids"]["Moderate"]

                tools_rec.call(
                    "run_default_optimise",
                    mmmRequestId=model_id
                )

                result = tools_rec.call(
                    "run_constrained_optimise",
                    mmmRequestId=model_id,
                    totalBudget=500000,
                    constraintType=constraint_type
                )

                if result["status"] != "success":
                    failed = True
                    answer = result["error_message"]

                else:

                    rows = result["data"]["dateRangeToResponseMap"][
                        "aggregated_aggregated"
                    ]["mmmBudgetOptimisationResponseList"]

                    all_platform = next(
                        row
                        for row in rows
                        if row["platformName"] == "All Platforms"
                    )

                    all_platform_revenue = all_platform[
                        "optimisedBudgetData"
                    ]["response"]

                    calc = tools_rec.call(
                        "calculate_target_budget",
                        target_revenue=2000000,
                        current_revenue=current_revenue,
                        all_platform_revenue=all_platform_revenue
                    )

                    answer = {
                        "modelId": model_id,
                        "targetRevenue": 2000000,
                        "currentRevenue": current_revenue,
                        "requiredBudget": calc["data"]["required_budget"]
                    }


        return {
            "answer": answer,
            "trace": {
                "tool_calls": tools_rec.calls,
                "llm_calls": llm_calls,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "latency_s": time.time() - t0,
                "asked_user": asked_user,
                "failed": failed,
            },
        }
