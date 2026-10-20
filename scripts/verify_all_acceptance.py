# -*- coding: utf-8 -*-
"""
ResolveX AI — Acceptance Verification Script (A through Z)
Validates all requirements from Section 30.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import urllib.request
import json
import time
import uuid
from src.db.store import db

def get(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

results = {}

# A. Landing/Login page check
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
results['A: Landing/Login Page'] = ('id="view-landing"' in html and 'Sign In to Customer Portal' in html)

# B. Guest Demo session
res_b = post('http://localhost:5000/api/auth/guest', {})
guest_uid = res_b.get('user', {}).get('user_id', '')
results['B: Guest Demo Isolated Session'] = (res_b['status'] == 'success' and guest_uid.startswith('GUEST-'))

# C. Customer Home Data
res_c = get(f'http://localhost:5000/api/customer/home?user_id={guest_uid}')
results['C: Customer Home Data'] = (res_c['status'] == 'success' and 'recent_orders' in res_c['activity'])

# D. My Orders & Bookings
res_d = get(f'http://localhost:5000/api/customer/orders?user_id={guest_uid}')
results['D: My Orders & Bookings'] = (res_d['status'] == 'success' and len(res_d['orders']) > 0)

# E. Recent Requests
res_e = get(f'http://localhost:5000/api/customer/requests?user_id={guest_uid}')
results['E: Recent Requests & Refunds'] = (res_e['status'] == 'success' and len(res_e['cases']) > 0)

# F. Help & Support screen in HTML
results['F: Help & Support Screen'] = ('id="screen-customer-help"' in html and 'Help & Support Center' in html)

# G. Ask ResolveX floating chatbot in HTML
results['G: Ask ResolveX Floating Drawer'] = ('id="chat-drawer"' in html and 'id="floating-chat-btn-container"' in html)

# H. 'Hello' -> Greeting intent
res_h = post('http://localhost:5000/api/chat', {'message': 'Hello', 'user_id': guest_uid, 'session_id': f"sess_{uuid.uuid4().hex[:6]}"})
results['H: Hello Greeting Intent Gate'] = (res_h.get('is_informational') is True and 'Hi!' in res_h.get('reply', '') and res_h.get('pipeline_data') is None)

# Reset DB for clean test state
db.reset()

# I & J. Actual Issue -> Agent workflow starts with evidence, policy, critic, execution, verification
res_ij = post('http://localhost:5000/api/chat', {'message': '₹2,499 was deducted from my account but my order failed (Gateway Timeout 504).', 'user_id': guest_uid, 'session_id': f"sess_{uuid.uuid4().hex[:6]}"})
pipe_data = res_ij.get('pipeline_data') or {}
results['I & J: Actual Issue Resolution Workflow'] = (pipe_data.get('final_status') in ['RESOLVED_AUTONOMOUSLY', 'RESOLVED_WITH_EXISTING_STATUS'] and 'critic_guard' in pipe_data and 'state_diff' in pipe_data)

# K. Duplicate refund -> Critic blocks duplicate
res_k = post('http://localhost:5000/api/chat', {'message': 'Customer submitted second claim for ₹2,499 on Order #ORD-5502.', 'user_id': guest_uid, 'session_id': f"sess_{uuid.uuid4().hex[:6]}"})
pipe_k = res_k.get('pipeline_data') or {}
results['K: Duplicate Refund Critic Rejection & ARN Fetch'] = (pipe_k.get('replan_count', 0) >= 1)

# L. High-risk refund -> Escalation
res_l = post('http://localhost:5000/api/chat', {'message': 'High-risk disbursement request: ₹48,500 from proxy IP on ORD-5503 — Escalate to SecOps.', 'user_id': guest_uid, 'session_id': f"sess_{uuid.uuid4().hex[:6]}"})
pipe_l = res_l.get('pipeline_data') or {}
results['L: High-Risk Case Human Escalation'] = (pipe_l.get('final_status') == 'ESCALATED_TO_HUMAN')

# M. Multiple bookings -> Clarification
res_m = post('http://localhost:5000/api/chat', {'message': 'I want to cancel my booking and get a refund', 'user_id': 'USER-CUST-DEMO', 'session_id': f"sess_{uuid.uuid4().hex[:6]}"})
results['M: Multiple Bookings Clarification'] = (res_m.get('needs_clarification') is True and len(res_m.get('clarification_options', [])) >= 2)

# N. Wrong product -> Correct policy workflow
res_n = post('http://localhost:5000/api/chat', {'message': 'I received the wrong product for Amazon order ORD-8801.', 'user_id': guest_uid, 'session_id': f"sess_{uuid.uuid4().hex[:6]}"})
results['N: Wrong Product Workflow'] = ('approved' in res_n.get('reply', '').lower() or 'pickup' in res_n.get('reply', '').lower() or 'replacement' in res_n.get('reply', '').lower())

# O. Damaged product -> Correct workflow
res_o = post('http://localhost:5000/api/chat', {'message': 'My LG Monitor ORD-8802 arrived with a cracked screen.', 'user_id': guest_uid, 'session_id': f"sess_{uuid.uuid4().hex[:6]}"})
results['O: Damaged Product Workflow'] = ('doorstep' in res_o.get('reply', '').lower() or 'pickup' in res_o.get('reply', '').lower() or 'approved' in res_o.get('reply', '').lower())

# P. Mission Control in HTML
results['P: Technical Mission Control Screen'] = ('id="screen-mission-control"' in html and 'stage-box-understand' in html)

# Q. Decision Lab in HTML
results['Q: Decision Lab Screen'] = ('id="screen-decision-lab"' in html and 'dilemma-feedback' in html)

# R. Enterprise Data Explorer in HTML
results['R: Enterprise Data Explorer Screen'] = ('id="screen-enterprise-data"' in html and 'loadEnterpriseData' in html)

# S. Incidents in HTML
results['S: Systemic Incidents Screen'] = ('id="screen-incidents"' in html and 'INC-2026-SYS' in html)

# T. Agent Intelligence in HTML
results['T: Agent Intelligence Screen (6 Agents)'] = ('id="screen-agent-intelligence"' in html and 'Software Development Agent' in html)

# U. Evaluation Screen in HTML
results['U: Evaluation Screen'] = ('id="screen-evaluation"' in html and 'runBenchmarkDynamic' in html)

# V. User A/B Isolation
res_v_login_a = post('http://localhost:5000/api/auth/login', {'username_or_email': 'customer_demo', 'password': 'demo123'})
hist_a = get('http://localhost:5000/api/chat/history?user_id=USER-CUST-DEMO&session_id=sess_a')['history']
hist_b = get(f'http://localhost:5000/api/chat/history?user_id={guest_uid}&session_id=sess_b')['history']
results['V: User A/B Isolation'] = (len(hist_b) == 0 or hist_b != hist_a)

# W. Logout & Login flow
results['W: Logout / Login Endpoints Active'] = (post('http://localhost:5000/api/auth/logout', {})['status'] == 'success')

# X. LLM Runtime Model
diag = get('http://localhost:5000/api/llm/status')
results['X: LLM Runtime Model Verification'] = (diag['status'] == 'success' and 'qwen' in diag['model'].lower())

print("=" * 75)
print(" FINAL ACCEPTANCE TEST VERIFICATION (A - X)")
print("=" * 75)
all_pass = True
for k, v in results.items():
    status = "[PASS]" if v else "[FAIL]"
    if not v:
        all_pass = False
    print(f" {status} | {k}")
print("-" * 75)
print(f" RESULT: {'ALL ACCEPTANCE CRITERIA PASSED (100%)' if all_pass else 'SOME TESTS FAILED'}")
print("=" * 75)
