# -*- coding: utf-8 -*-
"""
End-to-End Real Browser Playwright Authentication Regression Test Suite
Executes the exact 10-step browser authentication sequence requested by the user.
"""

import sys
import time
from playwright.sync_api import sync_playwright

def run_browser_auth_tests():
    print("=" * 75)
    print(" RESOLVEX AI — REAL BROWSER AUTHENTICATION E2E TEST (TESTS 1 - 10)")
    print("=" * 75)

    console_errors = []
    page_errors = []

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # -------------------------------------------------------------
        # TEST 1: Open http://localhost:5000 -> Landing page appears
        # -------------------------------------------------------------
        t0 = time.time()
        page.goto("http://localhost:5000", wait_until="networkidle")
        time.sleep(0.5)

        landing_visible = page.locator("#view-landing").is_visible()
        chassis_hidden = not page.locator("#app-chassis").is_visible()
        t1_pass = landing_visible and chassis_hidden
        results.append({
            "test": "TEST 1",
            "name": "Landing/Authentication View on Initial Load",
            "passed": t1_pass,
            "latency": f"{round(time.time() - t0, 3)}s",
            "details": f"Landing visible: {landing_visible}, App Chassis hidden: {chassis_hidden}"
        })

        # -------------------------------------------------------------
        # TEST 2: Click Demo Customer / Load Demo -> Customer dashboard opens
        # -------------------------------------------------------------
        t0 = time.time()
        page.click("#btn-quick-demo")
        page.wait_for_selector("#app-chassis:not(.hidden)", timeout=5000)
        time.sleep(0.5)

        chassis_vis = page.locator("#app-chassis").is_visible()
        disp_name = page.locator("#user-display-name").inner_text()
        t2_pass = chassis_vis and "Rahul" in disp_name
        results.append({
            "test": "TEST 2",
            "name": "Click Demo Customer / Load Demo",
            "passed": t2_pass,
            "latency": f"{round(time.time() - t0, 3)}s",
            "details": f"Dashboard opened with user: {disp_name}"
        })

        # -------------------------------------------------------------
        # TEST 3: Logout -> Landing page returns
        # -------------------------------------------------------------
        t0 = time.time()
        page.click("button[title='Log Out']")
        page.wait_for_selector("#view-landing:not(.hidden)", timeout=5000)
        time.sleep(0.5)

        landing_vis = page.locator("#view-landing").is_visible()
        token_cleared = page.evaluate("() => localStorage.getItem('resolvex_user')") is None
        t3_pass = landing_vis and token_cleared
        results.append({
            "test": "TEST 3",
            "name": "Logout Destroys Session & Restores Landing View",
            "passed": t3_pass,
            "latency": f"{round(time.time() - t0, 3)}s",
            "details": f"Landing restored: {landing_vis}, LocalStorage purged: {token_cleared}"
        })

        # -------------------------------------------------------------
        # TEST 4: Login as Jaydev with correct credentials
        # -------------------------------------------------------------
        t0 = time.time()
        page.fill("#landing-ident", "jaydev")
        page.fill("#landing-pwd", "demo123")
        page.click("#customer-login-submit")
        page.wait_for_selector("#app-chassis:not(.hidden)", timeout=5000)
        time.sleep(0.8)

        disp_jaydev = page.locator("#user-display-name").inner_text()
        t4_pass = "Jaydev" in disp_jaydev
        results.append({
            "test": "TEST 4",
            "name": "Login as Jaydev with Correct Credentials",
            "passed": t4_pass,
            "latency": f"{round(time.time() - t0, 3)}s",
            "details": f"Authenticated successfully: {disp_jaydev}"
        })

        # -------------------------------------------------------------
        # TEST 5: Logout from Jaydev
        # -------------------------------------------------------------
        t0 = time.time()
        page.click("button[title='Log Out']")
        page.wait_for_selector("#view-landing:not(.hidden)", timeout=5000)
        time.sleep(0.5)

        t5_pass = page.locator("#view-landing").is_visible()
        results.append({
            "test": "TEST 5",
            "name": "Logout from Jaydev Account",
            "passed": t5_pass,
            "latency": f"{round(time.time() - t0, 3)}s",
            "details": f"Landing view restored: {t5_pass}"
        })

        # -------------------------------------------------------------
        # TEST 6: Login as Rajvi with correct credentials
        # -------------------------------------------------------------
        t0 = time.time()
        page.click("#btn-quick-rajvi")
        page.wait_for_selector("#app-chassis:not(.hidden)", timeout=5000)
        time.sleep(0.8)

        disp_rajvi = page.locator("#user-display-name").inner_text()
        t6_pass = "Rajvi" in disp_rajvi
        results.append({
            "test": "TEST 6",
            "name": "Login as Rajvi (Strict Isolation)",
            "passed": t6_pass,
            "latency": f"{round(time.time() - t0, 3)}s",
            "details": f"Authenticated successfully: {disp_rajvi}"
        })

        # -------------------------------------------------------------
        # TEST 7: Logout from Rajvi
        # -------------------------------------------------------------
        t0 = time.time()
        page.click("button[title='Log Out']")
        page.wait_for_selector("#view-landing:not(.hidden)", timeout=5000)
        time.sleep(0.5)

        t7_pass = page.locator("#view-landing").is_visible()
        results.append({
            "test": "TEST 7",
            "name": "Logout from Rajvi Account",
            "passed": t7_pass,
            "latency": f"{round(time.time() - t0, 3)}s",
            "details": f"Landing view restored: {t7_pass}"
        })

        # -------------------------------------------------------------
        # TEST 8: Try incorrect password -> Visibly fails with error message
        # -------------------------------------------------------------
        t0 = time.time()
        page.fill("#landing-ident", "jaydev")
        page.fill("#landing-pwd", "wrong_password_999")
        page.click("#customer-login-submit")
        time.sleep(0.8)

        err_vis = page.locator("#customer-login-error").is_visible()
        err_msg = page.locator("#customer-login-error").inner_text() if err_vis else ""
        still_landing = page.locator("#view-landing").is_visible()
        no_pwd_leak = "demo123" not in err_msg and "wrong_password_999" not in err_msg
        t8_pass = err_vis and "Invalid credentials" in err_msg and still_landing and no_pwd_leak
        results.append({
            "test": "TEST 8",
            "name": "Incorrect Password Rejection & Error Display",
            "passed": t8_pass,
            "latency": f"{round(time.time() - t0, 3)}s",
            "details": f"Error visible: '{err_msg}', Blocked dashboard entry: {still_landing}"
        })

        # -------------------------------------------------------------
        # TEST 9: Guest Mode -> Isolated guest session
        # -------------------------------------------------------------
        t0 = time.time()
        page.click("#btn-guest-login")
        page.wait_for_selector("#app-chassis:not(.hidden)", timeout=5000)
        time.sleep(0.8)

        guest_role = page.locator("#user-role-label").inner_text()
        guest_reset_vis = page.locator("#guest-reset-badge").is_visible()
        t9_pass = "Guest" in guest_role and guest_reset_vis
        results.append({
            "test": "TEST 9",
            "name": "1-Click Guest Mode Session Creation",
            "passed": t9_pass,
            "latency": f"{round(time.time() - t0, 3)}s",
            "details": f"Role: {guest_role}, Reset demo badge active: {guest_reset_vis}"
        })

        # -------------------------------------------------------------
        # TEST 10: Evaluator access -> Evaluator Mission Control opens
        # -------------------------------------------------------------
        t0 = time.time()
        # Logout from guest
        page.click("button[title='Log Out']")
        page.wait_for_selector("#view-landing:not(.hidden)", timeout=5000)

        # Click Evaluator tab
        page.click("#tab-btn-evaluator")
        time.sleep(0.3)
        page.click("#evaluator-login-submit")
        page.wait_for_selector("#app-chassis:not(.hidden)", timeout=5000)
        time.sleep(0.8)

        mc_vis = page.locator("#screen-mission-control").is_visible()
        eval_name = page.locator("#user-display-name").inner_text()
        switch_btn_txt = page.locator("#header-switch-view-label").inner_text()
        t10_pass = mc_vis and "Elena" in eval_name and "Switch to Customer View" in switch_btn_txt
        results.append({
            "test": "TEST 10",
            "name": "Evaluator Authentication & Mission Control Launch",
            "passed": t10_pass,
            "latency": f"{round(time.time() - t0, 3)}s",
            "details": f"Mission Control active: {mc_vis}, Evaluator: {eval_name}, Switch: '{switch_btn_txt}'"
        })

        browser.close()

    print("\n" + "=" * 75)
    print(" REAL BROWSER AUTHENTICATION RESULTS")
    print("=" * 75)
    passed_count = sum(1 for r in results if r["passed"])
    for r in results:
        tag = "[PASS]  " if r["passed"] else "[FAIL] *"
        print(f" {tag} | {r['test']}: {r['name']:<48} | {r['latency']}")
        print(f"            Details: {r['details']}")
    print("-" * 75)
    print(f" OVERALL: {passed_count}/{len(results)} Browser Tests Passed ({passed_count/len(results)*100:.1f}%)")
    print(f" Console Errors: {len(console_errors)}, Unhandled Page Exceptions: {len(page_errors)}")
    if page_errors:
        print(" Page Errors:", page_errors)
    if console_errors:
        print(" Console Errors:", console_errors)
    print("=" * 75 + "\n")

    return results, passed_count == len(results)

if __name__ == "__main__":
    _, all_ok = run_browser_auth_tests()
    if not all_ok:
        sys.exit(1)
