#!/usr/bin/env python3
"""AI cost model for vn-news-monitor (phase 2).

Usage: python3 -I scripts/cost_model.py > evidence/p2-thiet-ke/cost-model-output.md

Prices: USD per million tokens, read from
https://platform.claude.com/docs/en/about-claude/pricing.md on 2026-10-22
(excerpt in evidence/p2-thiet-ke/pricing-2026-10-22.txt).
Token counts are assumptions (GIA DINH) until phase 4 measures real usage.
Edit the constants below and run again.
"""

PRICES = {  # model: (input, output) per MTok, standard (non-batch) rate
    "claude-haiku-5-5": (0.10, 0.50),  # prompts up to 100,000 tokens
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
    "claude-haiku-4-5": (1.00, 5.00),
}

# Classification call (Information Extractor + Anthropic Chat Model)
SYSTEM_PROMPT_TOKENS = 1200  # Vietnamese rubric + rules
SCHEMA_OVERHEAD_TOKENS = 406 + 700  # tool-use system prompt (pricing page) + JSON schema
ITEM_INPUT_TOKENS = 300  # source, title, snippet <= 500 chars, ids
ITEM_OUTPUT_TOKENS = 180  # one JSON object with summary_vi (<= 40 words)
CALL_OUTPUT_OVERHEAD = 100  # array wrapper, tool_use block
THINKING_TOKENS_PER_CALL = 0  # Thinking Mode = Disabled; see stress row below

# Digest call: reads summary_vi only, writes the digest body
DIGEST_RUNS_PER_DAY = 2
DIGEST_PROMPT_TOKENS = 1500
DIGEST_ITEM_TOKENS = 80
DIGEST_ITEMS = 40
DIGEST_OUTPUT_TOKENS = 1500

TRADING_DAYS_PER_MONTH = 22
SCENARIOS = {"thap": 30, "vua": 80, "cao": 200}  # AI items per day; cao = MAX_AI_ITEMS_PER_DAY


def call_cost(model, tokens_in, tokens_out):
    p_in, p_out = PRICES[model]
    return tokens_in * p_in / 1e6 + tokens_out * p_out / 1e6


def classify_cost_per_day(model, items, batch_size, thinking=THINKING_TOKENS_PER_CALL):
    calls = -(-items // batch_size)  # ceil
    tokens_in = calls * (SYSTEM_PROMPT_TOKENS + SCHEMA_OVERHEAD_TOKENS) + items * ITEM_INPUT_TOKENS
    tokens_out = calls * (CALL_OUTPUT_OVERHEAD + thinking) + items * ITEM_OUTPUT_TOKENS
    return calls, tokens_in, tokens_out, call_cost(model, tokens_in, tokens_out)


def digest_cost_per_day(model):
    tokens_in = DIGEST_RUNS_PER_DAY * (DIGEST_PROMPT_TOKENS + DIGEST_ITEMS * DIGEST_ITEM_TOKENS)
    tokens_out = DIGEST_RUNS_PER_DAY * DIGEST_OUTPUT_TOKENS
    return tokens_in, tokens_out, call_cost(model, tokens_in, tokens_out)


def usd(x):
    return f"{x:.4f}"


def main():
    print("## Ket qua tinh (sinh tu scripts/cost_model.py)\n")
    print("### 1. Phan loai, theo kich ban va cach goi\n")
    print("| Kich ban | Tin/ngay | Mo hinh | Gom lo | Luot goi/ngay | Token vao/ngay | Token ra/ngay | USD/ngay | USD/thang (22 ngay) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for name, items in SCENARIOS.items():
        for model, batch in (("claude-haiku-5-5", 10), ("claude-haiku-5-5", 1), ("claude-sonnet-5-5", 10)):
            calls, t_in, t_out, cost = classify_cost_per_day(model, items, batch)
            print(f"| {name} | {items} | `{model}` | {batch} | {calls} | {t_in:,} | {t_out:,} | {usd(cost)} | {usd(cost * TRADING_DAYS_PER_MONTH)} |")
    print("\n### 2. Kiem tra do nhay: neu mo hinh van suy nghi (thinking) 1.000 token moi luot\n")
    print("| Kich ban | Mo hinh | Gom lo | USD/ngay khi tat thinking | USD/ngay khi co thinking | Chenh lech |")
    print("|---|---|---|---|---|---|")
    for name, items in SCENARIOS.items():
        base = classify_cost_per_day("claude-haiku-5-5", items, 10)[3]
        think = classify_cost_per_day("claude-haiku-5-5", items, 10, thinking=1000)[3]
        print(f"| {name} | `claude-haiku-5-5` | 10 | {usd(base)} | {usd(think)} | x{think / base:.2f} |")
    print("\n### 3. Ban tin tong hop (2 lan/ngay)\n")
    print("| Mo hinh | Token vao/ngay | Token ra/ngay | USD/ngay | USD/thang (22 ngay) |")
    print("|---|---|---|---|---|")
    for model in ("claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"):
        t_in, t_out, cost = digest_cost_per_day(model)
        print(f"| `{model}` | {t_in:,} | {t_out:,} | {usd(cost)} | {usd(cost * TRADING_DAYS_PER_MONTH)} |")
    print("\n### 4. Tong theo cau hinh mac dinh (phan loai Haiku 5.5 gom 10 + ban tin Sonnet 5.5)\n")
    print("| Kich ban | USD/ngay | USD/thang (22 ngay) |")
    print("|---|---|---|")
    digest = digest_cost_per_day("claude-sonnet-5-5")[2]
    for name, items in SCENARIOS.items():
        total = classify_cost_per_day("claude-haiku-5-5", items, 10)[3] + digest
        print(f"| {name} | {usd(total)} | {usd(total * TRADING_DAYS_PER_MONTH)} |")


if __name__ == "__main__":
    main()
