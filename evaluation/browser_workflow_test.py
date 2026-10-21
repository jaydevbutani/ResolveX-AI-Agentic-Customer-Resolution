# -*- coding: utf-8 -*-
"""
End-to-End Real Browser Workflow Test:
Tests 1 complete customer issue resolution through the multi-agent engine,
verifies customer explainability accordion, and checks live agent contribution trace.
"""

import sys
import time
from playwright.sync_api import sync_playwright

def run_workflow_e2e_test():
    print("=" * 75)
    print(" RESOLVEX AI — END-TO-END WORKFLOW & AGENT TRACE TEST")
    print("=" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Open landing page
        page.goto("http://localhost:5000", wait_until="networkidle")
        time.sleep(0.5)

        # 2. Click Demo Customer
        page.click("#btn-quick-demo")
        page.wait_for_selector("#app-chassis:not(.hidden)", timeout=5000)
        time.sleep(0.8)

        # 3. Enter issue on Customer Home and submit
        issue_text = "₹2,499 was deducted from my account but order failed with Gateway Timeout 504."
        page.fill("#cust-home-input", issue_text)
        page.click("button[onclick='submitCustomerIssueFromHome()']")

        # 4. Wait for drawer to open and resolution response to appear
        page.wait_for_selector("#chat-drawer:not(.hidden)", timeout=5000)
        # Wait for bot response container
        page.wait_for_selector("#drawer-messages .rounded-2xl.border-slate-200", timeout=15000)
        time.sleep(1.0)

        drawer_html = page.locator("#drawer-messages").inner_html()
        has_resolved = "Resolved" in drawer_html or "RESOLVED" in drawer_html or "Disbursed" in drawer_html or "Refund" in drawer_html
        has_refund = "Refund" in drawer_html or "RF-" in drawer_html or "ARN" in drawer_html
        has_accordion = "How did ResolveX decide?" in drawer_html

        print(f" -> Resolution response received: {has_resolved}")
        print(f" -> Bank Reference/ARN generated: {has_refund}")
        print(f" -> Explainability Accordion present: {has_accordion}")

        # 5. Log out from Customer and Log in as Evaluator
        page.click("button[onclick='toggleChatDrawer(false)']")
        time.sleep(0.3)
        page.click("button[title='Log Out']")
        page.wait_for_selector("#view-landing:not(.hidden)", timeout=5000)

        page.click("#tab-btn-evaluator")
        time.sleep(0.3)
        page.click("#evaluator-login-submit")
        page.wait_for_selector("#screen-mission-control:not(.hidden)", timeout=5000)
        time.sleep(1.0)

        # 6. Check Section 4: Agent Contribution Trace
        planner_stat = page.locator("#trace-planner-status").inner_text()
        research_stat = page.locator("#trace-research-status").inner_text()
        critic_stat = page.locator("#trace-critic-status").inner_text()
        executor_stat = page.locator("#trace-executor-status").inner_text()
        sda_stat = page.locator("#trace-sda-status").inner_text()

        print(f" -> Planner Agent Status: {planner_stat}")
        print(f" -> Research Agent Status: {research_stat}")
        print(f" -> Critic Agent Status: {critic_stat}")
        print(f" -> Executor Agent Status: {executor_stat}")
        print(f" -> Software Dev Agent Status: {sda_stat}")

        trace_ok = (
            planner_stat != "" and
            research_stat != "" and
            critic_stat != "" and
            executor_stat != "" and
            sda_stat == "STANDBY"
        )

        browser.close()

        success = has_resolved and has_refund and has_accordion and trace_ok
        print("-" * 75)
        print(f" WORKFLOW & TRACE TEST RESULT: {'SUCCESS (PASS)' if success else 'FAILED'}")
        print("=" * 75)
        return success

if __name__ == "__main__":
    ok = run_workflow_e2e_test()
    if not ok:
        sys.exit(1)
