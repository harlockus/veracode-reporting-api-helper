#!/usr/bin/env python3
import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
from rich.console import Console
from rich.prompt import Prompt

# 🔐 HMAC-BASED HTTPie CALL
def call_httpie(method, url, input_json=None):
    cmd = ["http", "--body", "-A", "veracode_hmac", method, url]
    proc = subprocess.run(
        cmd,
        input=json.dumps(input_json) if input_json is not None else None,
        text=True,
        capture_output=True
    )
    if proc.returncode != 0:
        console.log(f"[red]❌ HTTPie error[/red] {method} {url}: {proc.stderr.strip()}")
        sys.exit(proc.returncode)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        console.log(f"[red]❌ JSON parse error:[/red] {e}")
        sys.exit(1)

def fetch_interval(start_dt, end_dt, console):
    """Run one FINDINGS report for this interval, wait for completion, return list."""
    console.log(f"[cyan]🔄 Submitting report[/cyan] {start_dt} → {end_dt}")
    payload = {
        "report_type": "FINDINGS",
        "last_updated_start_date": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "last_updated_end_date":   end_dt.strftime("%Y-%m-%d %H:%M:%S")
    }
    resp = call_httpie("POST", "https://api.veracode.com/appsec/v1/analytics/report", payload)

    report_obj = resp.get("_embedded", resp)
    report_id  = report_obj.get("id")
    if not report_id:
        raise RuntimeError(f"No report ID returned: {resp!r}")

    with console.status(f"[green]⏳ Polling report [bold]{report_id}[/bold]...", spinner="dots"):
        while True:
            full       = call_httpie("GET", f"https://api.veracode.com/appsec/v1/analytics/report/{report_id}")
            status_obj = full.get("_embedded", full)
            status     = status_obj.get("status")
            if status in ("SUBMITTED", "PROCESSING"):
                time.sleep(2)
                continue
            if status not in ("SUCCESS", "COMPLETED"):
                raise RuntimeError(f"Report {report_id} failed: {status}")
            break

    console.log(f"[bold green]✅ Report {report_id} done ({status})[/bold green]")
    findings = status_obj.get("findings", [])
    console.log(f"[magenta]📊 Retrieved[/magenta] {len(findings)} findings.")
    return findings

def main():
    parser = argparse.ArgumentParser(description="Fetch Veracode FINDINGS in 6-month chunks")
    parser.add_argument("--start-date", required=True,
                        help="Global start datetime (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--end-date",
                        help="Global end datetime (YYYY-MM-DD HH:MM:SS), defaults to now")
    parser.add_argument("--output-dir",
                        default="/Users/amazzarini/TECNIMONT_FINDINGS_API",
                        help="Where to write veracode_findings.xlsx")
    args = parser.parse_args()

    global console
    console = Console()
    console.print("[bold blue]🚀 Starting Veracode FINDINGS export[/bold blue]")

    start = datetime.strptime(args.start_date, "%Y-%m-%d %H:%M:%S")
    end   = datetime.strptime(args.end_date,   "%Y-%m-%d %H:%M:%S") if args.end_date else datetime.now()

    # build 6-month windows
    intervals = []
    cur = start
    while cur < end:
        nxt = cur + relativedelta(months=6)
        intervals.append((cur, min(nxt, end)))
        cur = min(nxt, end)

    all_findings = []
    total = len(intervals)
    for idx, (s, e) in enumerate(intervals, 1):
        console.print(f"[yellow]🎯 Interval {idx}/{total}:[/yellow] {s} → {e}")
        slice_data = fetch_interval(s, e, console)
        all_findings.extend(slice_data)

    if not all_findings:
        console.print("[red]⚠️ No findings returned.[/red]")
        sys.exit(0)

    # Load into DataFrame (no dedupe)
    df = pd.DataFrame.from_records(all_findings)

    # Prompt for app_name filter
    app_choice = Prompt.ask(
        "[bold]❔ Enter an app_name to filter by[/bold] (leave blank for all)",
        default=""
    ).strip()
    if app_choice:
        console.print(f"[cyan]🔍 Filtering to app_name=[/cyan] [bold]{app_choice}[/bold]")
        df = df[df.get("app_name", "") == app_choice]
    else:
        console.print("[cyan]📋 No filter applied; exporting all apps[/cyan]")

    # Write Excel
    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, "veracode_findings.xlsx")
    console.log(f"[cyan]📝 Writing to Excel[/cyan] {out_path}")
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    console.print("[bold green]✅ Export complete![/bold green]")

if __name__ == "__main__":
    main()
