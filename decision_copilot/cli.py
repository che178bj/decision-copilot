"""
Decision Co-Pilot CLI
命令列介面
"""
import click
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from rich.markdown import Markdown

from .analyzer import DecisionAnalyzer
from .storage import DecisionStorage

console = Console()


def print_header():
    """印出標題"""
    console.print(Panel.fit(
        "[bold cyan]🔮 Decision Co-Pilot[/bold cyan]\n[dim]您的 AI 決策小幫手[/dim]",
        border_style="cyan"
    ))


def print_analysis(analysis: dict):
    """印出分析結果"""
    # 建議
    rec_color = "green" if "積極" in analysis["recommendation"] or "可以" in analysis["recommendation"] else "yellow"
    console.print(f"\n[bold {rec_color}]🎯 最終建議：【{analysis['recommendation']}】[/bold {rec_color}]")
    console.print(f"[dim]{analysis['recommendation_text']}[/dim]\n")
    
    # 利弊分析
    if analysis["pros"]:
        console.print("[bold green]✅ 優點：[/bold green]")
        for pro in analysis["pros"]:
            console.print(f"  • {pro}")
    
    if analysis["cons"]:
        console.print("\n[bold red]⚠️ 缺點：[/bold red]")
        for con in analysis["cons"]:
            console.print(f"  • {con}")


def start_decision_flow():
    """啟動決策流程"""
    print_header()
    
    # 輸入問題
    console.print("\n請描述您面臨的決定：")
    question = console.input("→ ")
    
    if not question.strip():
        console.print("[yellow]問題不能為空，請重新輸入[/yellow]")
        return
    
    # 初始化分析器與儲存
    analyzer = DecisionAnalyzer()
    storage = DecisionStorage()
    
    # 偵測類型
    category = analyzer.detect_category(question)
    console.print(f"\n[dim]偵測到決策類型：{category}[/dim]\n")
    
    # 收集問題
    answers = {}
    all_questions = analyzer.get_questions(category, answers)
    
    for q in all_questions:
        console.print(f"[bold]❓ {q}[/bold]")
        answer = console.input("→ ")
        if answer.strip():
            # 提取關鍵詞作為 key
            key = q.split("（")[0].strip()
            answers[key] = answer.strip()
    
    # 分析
    analysis = analyzer.analyze(question, answers, category)
    
    # 輸出結果
    print_analysis(analysis)
    
    # 儲存決策
    decision_id = storage.add_decision(question, answers, analysis, analysis["recommendation"])
    console.print(f"\n[dim]💾 決策已儲存！ID: {decision_id}[/dim]")
    
    # 回顧提醒
    console.print("\n[dim]⚠️ 提醒：最終決定權在您手中，這只是參考[/dim]")


def list_decisions():
    """列出所有決策"""
    storage = DecisionStorage()
    decisions = storage.list_decisions()
    
    if not decisions:
        console.print("[yellow]尚無決策記錄[/yellow]")
        return
    
    table = Table(title="📋 決策列表")
    table.add_column("ID", style="cyan")
    table.add_column("問題", style="white")
    table.add_column("建議", style="green")
    table.add_column("狀態", style="yellow")
    table.add_column("日期", style="dim")
    
    for d in reversed(decisions):
        status_emoji = {
            "pending": "⏳ 待執行",
            "done": "✅ 已完成",
            "abandoned": "❌ 已放棄"
        }
        date = d["created_at"][:10]
        table.add_row(
            str(d["id"]),
            d["question"][:40] + "..." if len(d["question"]) > 40 else d["question"],
            d["recommendation"],
            status_emoji.get(d["status"], d["status"]),
            date
        )
    
    console.print(table)


def review_decision(decision_id: int):
    """回顧特定決策"""
    storage = DecisionStorage()
    decision = storage.get_decision(decision_id)
    
    if not decision:
        console.print(f"[red]找不到 ID {decision_id} 的決策[/red]")
        return
    
    console.print(Panel.fit(
        f"[bold]問題：[/bold]{decision['question']}",
        title=f"📝 決策 #{decision_id}",
        border_style="cyan"
    ))
    
    console.print(f"\n[bold]❓ 您的回答：[/bold]")
    for key, value in decision["answers"].items():
        console.print(f"  • {key}: {value}")
    
    print_analysis(decision["analysis"])
    
    # 更新狀態
    console.print("\n[bold]請問您後續結果是？[/bold]")
    console.print("1. ✅ 已執行/已完成")
    console.print("2. ❌ 已放棄/沒做")
    console.print("3. ⏳ 還在考慮中")
    
    choice = console.input("→ ")
    
    if choice == "1":
        storage.update_status(decision_id, "done", "已執行")
        console.print("[green]已更新為「已完成」！[/green]")
    elif choice == "2":
        storage.update_status(decision_id, "abandoned", "已放棄")
        console.print("[yellow]已更新為「已放棄」！[/yellow]")
    else:
        console.print("[dim]好的，維持待執行狀態[/dim]")


def show_stats():
    """顯示統計"""
    storage = DecisionStorage()
    stats = storage.get_statistics()
    
    table = Table(title="📊 決策統計")
    table.add_column("項目", style="cyan")
    table.add_column("數量", style="white")
    
    table.add_row("總決策數", str(stats["total"]))
    table.add_row("待執行", str(stats["pending"]))
    table.add_row("已完成", str(stats["done"]))
    table.add_row("已放棄", str(stats["abandoned"]))
    
    if stats["done"] > 0:
        table.add_row("採納率", f"{stats['adoption_rate']:.1f}%")
    
    console.print(table)


@click.group()
def cli():
    """🔮 Decision Co-Pilot - 您的 AI 決策小幫手"""
    pass


@cli.command()
def start():
    """開始新的決策分析"""
    start_decision_flow()


@cli.command()
def list():
    """列出所有決策"""
    list_decisions()


@cli.command()
@click.argument("decision_id", type=int)
def review(decision_id):
    """回顧特定決策"""
    review_decision(decision_id)


@cli.command()
def stats():
    """顯示決策統計"""
    show_stats()


@cli.command()
@click.argument("decision_id", type=int)
@click.argument("status")
def status(decision_id, status):
    """更新決策狀態 (pending/done/abandoned)"""
    storage = DecisionStorage()
    storage.update_status(decision_id, status)
    console.print(f"[green]已更新 ID {decision_id} 為 {status}[/green]")


def main():
    """主入口"""
    if len(sys.argv) == 1:
        # 沒有參數，啟動決策流程
        start_decision_flow()
    else:
        cli()


if __name__ == "__main__":
    main()
