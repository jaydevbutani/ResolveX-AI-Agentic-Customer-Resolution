# -*- coding: utf-8 -*-
"""
Generate the complete ResolveX AI Hybrid HTML:
Restores the full original technical dashboard UI while integrating the customer experience.
"""

import os
import re

if os.path.exists('frontend/index_original_backup.html'):
    with open('frontend/index_original_backup.html', 'r', encoding='utf-8') as f:
        orig = f.read()
else:
    import subprocess
    orig = subprocess.check_output(['git', 'show', '51ffe9a:frontend/index.html'], text=True, encoding='utf-8')

# 1. HEAD
head_end = orig.find('</head>')
head_part = orig[:head_end]

custom_extra_styles = """
    /* Hybrid Layer Extra Styles */
    .chat-bubble-user {
      background-color: #04060a;
      color: #ffffff;
      border-radius: 1.25rem 1.25rem 0.25rem 1.25rem;
    }
    .chat-bubble-bot {
      background-color: #ffffff;
      color: #0f172a;
      border: 1px solid #e2e8f0;
      border-radius: 1.25rem 1.25rem 1.25rem 0.25rem;
    }
    .chat-drawer-backdrop {
      background: rgba(4, 6, 10, 0.55);
      backdrop-filter: blur(4px);
    }
    .badge-status-resolved {
      background: #bff365;
      color: #131f00;
      font-weight: 700;
    }
    .badge-status-escalated {
      background: #ffdad6;
      color: #ba1a1a;
      font-weight: 700;
    }
    .badge-status-processing {
      background: #eaedff;
      color: #283044;
      font-weight: 700;
    }
"""
head_combined = head_part.replace('</style>', custom_extra_styles + '\n  </style>') + '\n</head>'

# 2. LANDING VIEW (FIRST SCREEN ON LOAD)
landing_html = """
  <!-- ========================================================================= -->
  <!-- 1. LANDING & AUTHENTICATION VIEW (FIRST SCREEN ON LOAD)                   -->
  <!-- ========================================================================= -->
  <div id="view-landing" class="flex flex-col min-h-screen bg-slate-50">
    <!-- Landing Navigation -->
    <header class="h-20 bg-white border-b border-slate-200 px-6 sm:px-12 flex items-center justify-between sticky top-0 z-30 shadow-sm">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-secondary-fixed font-extrabold text-xl shadow-md">
          ⚡
        </div>
        <div class="flex flex-col">
          <span class="font-grotesk text-2xl font-bold tracking-tight text-slate-900 leading-none">ResolveX</span>
          <span class="text-[11px] font-semibold text-secondary tracking-wide uppercase mt-0.5">Autonomous Customer Resolution</span>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <button onclick="startGuestSession()" class="px-5 py-2.5 rounded-full bg-slate-900 text-secondary-fixed font-grotesk font-semibold text-xs hover:bg-slate-800 transition-all shadow-sm flex items-center gap-2">
          <span class="material-symbols-outlined text-[16px]">play_arrow</span>
          <span>Continue as Guest / Try Demo</span>
        </button>
        <button onclick="scrollToAuth('login')" class="px-5 py-2.5 rounded-full bg-primary text-secondary-fixed font-grotesk font-semibold text-xs hover:bg-primary/90 transition-all shadow-sm">
          Sign In
        </button>
      </div>
    </header>

    <!-- Hero Value Proposition -->
    <main class="flex-1 max-w-6xl w-full mx-auto px-6 py-12 flex flex-col gap-12">
      <div class="text-center max-w-3xl mx-auto flex flex-col gap-4 pt-6">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary-container/30 text-secondary border border-secondary/20 text-xs font-semibold mx-auto">
          <span class="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
          6-Agent Autonomous Execution Engine • Air-Gapped PoC
        </div>
        <h1 class="font-grotesk text-4xl sm:text-5xl font-extrabold text-slate-950 tracking-tight leading-tight">
          Resolve issues, <span class="text-secondary font-black">not just conversations.</span>
        </h1>
        <p class="text-base text-slate-600 leading-relaxed max-w-2xl mx-auto">
          Everyday customer problems require multiple disconnected systems to resolve. ResolveX coordinates 6 specialized agents to verify payments, check policies, prevent duplicates, and disburse refunds autonomously.
        </p>

        <!-- Fast Action CTAs -->
        <div class="flex flex-wrap items-center justify-center gap-4 pt-4">
          <button onclick="startGuestSession()" class="px-8 py-3.5 rounded-full bg-primary text-secondary-fixed font-grotesk font-bold text-sm hover:bg-primary/90 transition-all shadow-lg shadow-black/20 flex items-center gap-2">
            <span class="material-symbols-outlined text-[20px]">rocket_launch</span>
            <span>Try Instant Guest Demo</span>
          </button>
          <button onclick="scrollToAuth('login')" class="px-8 py-3.5 rounded-full bg-white text-slate-800 border border-slate-300 font-grotesk font-semibold text-sm hover:bg-slate-50 transition-all shadow-sm">
            Customer Login
          </button>
        </div>
      </div>

      <!-- Feature Highlights -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col gap-3">
          <div class="w-10 h-10 rounded-xl bg-slate-100 text-secondary-fixed bg-primary flex items-center justify-center font-bold">
            <span class="material-symbols-outlined text-[22px]">account_balance_wallet</span>
          </div>
          <h3 class="font-grotesk font-bold text-slate-900 text-base">Autonomous Disbursements</h3>
          <p class="text-xs text-slate-600 leading-relaxed">
            Payment verified on gateway but booking failed? ResolveX initiates genuine banking refunds with traceable ARNs in under 250ms.
          </p>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col gap-3">
          <div class="w-10 h-10 rounded-xl bg-slate-100 text-secondary-fixed bg-primary flex items-center justify-center font-bold">
            <span class="material-symbols-outlined text-[22px]">security</span>
          </div>
          <h3 class="font-grotesk font-bold text-slate-900 text-base">Critic Guard & Safety</h3>
          <p class="text-xs text-slate-600 leading-relaxed">
            The Critic Agent enforces idempotency tokens, blocks duplicate payout claims, and safely routes high-risk or ceiling-breaching cases to humans.
          </p>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col gap-3">
          <div class="w-10 h-10 rounded-xl bg-slate-100 text-secondary-fixed bg-primary flex items-center justify-center font-bold">
            <span class="material-symbols-outlined text-[22px]">hub</span>
          </div>
          <h3 class="font-grotesk font-bold text-slate-900 text-base">Service-Aware Connectors</h3>
          <p class="text-xs text-slate-600 leading-relaxed">
            Simulated connectors for RedBus, MakeMyTrip, Amazon, Flipkart, and Swiggy evaluate provider-specific cancellation windows and return policies.
          </p>
        </div>
      </div>

      <!-- Auth Card Section -->
      <div id="auth-section" class="max-w-md w-full mx-auto bg-white p-8 rounded-3xl border border-slate-200 shadow-xl flex flex-col gap-4">
        <!-- Access-Type Destination Switcher -->
        <div class="flex p-1 bg-slate-100 rounded-2xl border border-slate-200">
          <button type="button" id="tab-btn-customer" onclick="setAuthTab('customer')" class="flex-1 py-2.5 text-xs font-grotesk font-bold rounded-xl transition-all bg-white text-slate-900 shadow-sm flex items-center justify-center gap-1.5">
            <span class="material-symbols-outlined text-[16px]">person</span>
            <span>Customer</span>
          </button>
          <button type="button" id="tab-btn-evaluator" onclick="setAuthTab('evaluator')" class="flex-1 py-2.5 text-xs font-grotesk font-bold rounded-xl transition-all text-slate-500 hover:text-slate-800 flex items-center justify-center gap-1.5">
            <span class="material-symbols-outlined text-[16px]">terminal</span>
            <span>Evaluator</span>
          </button>
        </div>

        <!-- FORM 1: CUSTOMER ACCESS -->
        <div id="auth-panel-customer" class="flex flex-col gap-3.5">
          <div class="flex items-center justify-between border-b border-slate-100 pb-2">
            <div>
              <h2 class="font-grotesk font-bold text-base text-slate-900">Customer Sign In</h2>
              <span class="text-[11px] text-slate-500">Access your private orders & resolutions</span>
            </div>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Tenant-Isolated</span>
          </div>

          <form id="login-form-customer" onsubmit="handleCustomerLogin(event)" class="flex flex-col gap-3">
            <div id="customer-login-error" class="hidden p-2.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 font-medium"></div>

            <div class="flex flex-col gap-1">
              <label class="text-xs font-semibold text-slate-700">Username or Email</label>
              <input type="text" id="landing-ident" required class="px-4 py-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-primary" placeholder="Enter username or email (e.g. customer_demo or jaydev)..."/>
            </div>

            <div class="flex flex-col gap-1">
              <label class="text-xs font-semibold text-slate-700">Password</label>
              <input type="password" id="landing-pwd" required class="px-4 py-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-primary" placeholder="••••••••"/>
            </div>

            <button type="submit" id="customer-login-submit" class="w-full py-3 rounded-full bg-primary text-secondary-fixed font-grotesk font-bold text-xs hover:bg-primary/90 transition-all shadow-md mt-1">
              Sign In to Customer Portal
            </button>
          </form>

          <div class="relative flex py-1 items-center">
            <div class="flex-grow border-t border-slate-200"></div>
            <span class="flex-shrink mx-3 text-[11px] text-slate-400 font-semibold uppercase">Or</span>
            <div class="flex-grow border-t border-slate-200"></div>
          </div>

          <button type="button" onclick="startGuestSession()" class="w-full py-2.5 px-4 rounded-full bg-slate-900 hover:bg-slate-800 text-secondary-fixed text-xs font-grotesk font-bold transition-all shadow-sm flex items-center justify-center gap-2">
            <span class="material-symbols-outlined text-[16px]">play_arrow</span>
            <span>Continue as Guest / Try Demo</span>
          </button>

          <div class="text-[11px] text-slate-500 text-center pt-1 leading-relaxed">
            Your account data, orders, and resolution history are strictly isolated and private.
          </div>
        </div>

        <!-- FORM 2: EVALUATOR ACCESS -->
        <div id="auth-panel-evaluator" class="hidden flex flex-col gap-3.5">
          <div class="flex items-center justify-between border-b border-slate-100 pb-2">
            <div>
              <h2 class="font-grotesk font-bold text-base text-slate-900">Evaluator & Operations Console</h2>
              <span class="text-[11px] text-slate-500">Inspect multi-agent orchestration</span>
            </div>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-800">Staff / Arch</span>
          </div>

          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-600 leading-relaxed">
            Enter evaluator credentials to inspect the 6-agent StateGraph, live DAG execution logs, decision traces, and automated benchmark verification.
          </div>

          <form id="login-form-evaluator" onsubmit="handleEvaluatorLogin(event)" class="flex flex-col gap-3">
            <div id="evaluator-login-error" class="hidden p-2.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 font-medium"></div>

            <div class="flex flex-col gap-1">
              <label class="text-xs font-semibold text-slate-700">Evaluator Username</label>
              <input type="text" id="eval-ident" required value="evaluator" class="px-4 py-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-primary" placeholder="evaluator"/>
            </div>

            <div class="flex flex-col gap-1">
              <label class="text-xs font-semibold text-slate-700">Password</label>
              <input type="password" id="eval-pwd" required value="evaluator123" class="px-4 py-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-primary" placeholder="••••••••"/>
            </div>

            <button type="submit" id="evaluator-login-submit" class="w-full py-3 rounded-full bg-slate-900 text-secondary-fixed font-grotesk font-bold text-xs hover:bg-slate-800 transition-all shadow-md mt-1 flex items-center justify-center gap-1.5">
              <span class="material-symbols-outlined text-[16px]">terminal</span>
              <span>Enter Evaluator Console</span>
            </button>
          </form>

          <div class="text-[11px] text-slate-500 text-center pt-1 leading-relaxed">
            Evaluator credentials required. Unauthorized access is blocked by RBAC security gate.
          </div>
        </div>

      </div>
    </main>

    <!-- Footer with Discreet Evaluator Entry Point -->
    <footer class="bg-white border-t border-slate-200 px-6 sm:px-12 py-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4 mt-auto">
      <div>
        © 2026 ResolveX AI • Autonomous Customer Issue Resolution Engine • CA-3 Project
      </div>
      <div class="flex items-center gap-4">
        <button onclick="openEvaluatorPortal()" class="text-slate-600 hover:text-primary font-semibold flex items-center gap-1.5 transition-colors">
          <span class="material-symbols-outlined text-[16px]">terminal</span>
          <span>Evaluator & Admin Console</span>
        </button>
      </div>
    </footer>
  </div>
"""

# 3. SIDEBAR HTML (DARK OBSIDIAN CHASSIS)
sidebar_html = """
  <!-- ========================================================================= -->
  <!-- LEFT SIDEBAR: DARK OBSIDIAN CHASSIS (#1c1f24)                            -->
  <!-- ========================================================================= -->
  <aside class="fixed left-0 top-0 h-full w-72 bg-primary-container z-40 flex flex-col justify-between p-4 text-white border-r border-white/10 shadow-2xl">
    <div class="flex flex-col gap-6">
      
      <!-- Brand & Version -->
      <div class="flex items-center justify-between px-1 pt-2">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-secondary-fixed flex items-center justify-center font-extrabold text-on-secondary-fixed text-lg shadow-sm">
            ⚡
          </div>
          <span class="font-grotesk text-xl font-bold tracking-tight text-white">ResolveX</span>
        </div>
        <span id="sidebar-version-badge" class="font-grotesk text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#283044] text-[#c4c6cd] uppercase tracking-wider">
          AI-OPS v4.8
        </span>
      </div>

      <!-- Mode Indicator Tag -->
      <div class="px-1">
        <div id="sidebar-mode-indicator" class="flex items-center justify-between px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs">
          <span class="text-slate-300 font-grotesk font-semibold text-[11px]" id="sidebar-mode-label">Customer Portal</span>
          <span class="w-2 h-2 rounded-full bg-secondary-fixed" id="sidebar-mode-dot"></span>
        </div>
      </div>

      <!-- Navigation 1: CUSTOMER NAVIGATION (LAYER 1) -->
      <nav class="flex flex-col gap-1.5" id="sidebar-nav-customer">
        <button onclick="switchScreen('customer-home')" data-nav="customer-home" class="nav-btn w-full flex items-center justify-between px-4 py-2.5 rounded-full transition-all bg-secondary-fixed text-on-secondary-fixed font-grotesk font-bold shadow-sm">
          <div class="flex items-center gap-2.5">
            <span class="material-symbols-outlined text-[20px]">home</span>
            <span class="text-sm">Home</span>
          </div>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-secondary text-secondary-fixed">Active</span>
        </button>

        <button onclick="switchScreen('customer-orders')" data-nav="customer-orders" class="nav-btn w-full flex items-center gap-2.5 px-4 py-2.5 rounded-full text-[#c4c6cd] hover:bg-[#283044] hover:text-white transition-all font-grotesk font-semibold text-sm">
          <span class="material-symbols-outlined text-[20px]">shopping_bag</span>
          <span>My Orders & Bookings</span>
        </button>

        <button onclick="switchScreen('customer-requests')" data-nav="customer-requests" class="nav-btn w-full flex items-center gap-2.5 px-4 py-2.5 rounded-full text-[#c4c6cd] hover:bg-[#283044] hover:text-white transition-all font-grotesk font-semibold text-sm">
          <span class="material-symbols-outlined text-[20px]">receipt_long</span>
          <span>Recent Requests</span>
        </button>

        <button onclick="switchScreen('customer-help')" data-nav="customer-help" class="nav-btn w-full flex items-center gap-2.5 px-4 py-2.5 rounded-full text-[#c4c6cd] hover:bg-[#283044] hover:text-white transition-all font-grotesk font-semibold text-sm">
          <span class="material-symbols-outlined text-[20px]">support_agent</span>
          <span>Help & Support</span>
        </button>

        <button onclick="switchScreen('customer-account')" data-nav="customer-account" class="nav-btn w-full flex items-center gap-2.5 px-4 py-2.5 rounded-full text-[#c4c6cd] hover:bg-[#283044] hover:text-white transition-all font-grotesk font-semibold text-sm">
          <span class="material-symbols-outlined text-[20px]">account_circle</span>
          <span>Account</span>
        </button>
      </nav>

      <!-- Navigation 2: EVALUATOR TECHNICAL NAVIGATION (LAYER 2) -->
      <nav class="flex flex-col gap-1.5 hidden" id="sidebar-nav-evaluator">
        <button onclick="switchScreen('mission-control')" data-nav="mission-control" class="nav-btn w-full flex items-center justify-between px-4 py-2.5 rounded-full transition-all bg-secondary-fixed text-on-secondary-fixed font-grotesk font-bold shadow-sm">
          <div class="flex items-center gap-2.5">
            <span class="material-symbols-outlined text-[20px]">grid_view</span>
            <span class="text-sm">Mission Control</span>
          </div>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-secondary text-secondary-fixed">6 Online</span>
        </button>

        <button onclick="switchScreen('decision-lab')" data-nav="decision-lab" class="nav-btn w-full flex items-center gap-2.5 px-4 py-2.5 rounded-full text-[#c4c6cd] hover:bg-[#283044] hover:text-white transition-all font-grotesk font-semibold text-sm">
          <span class="material-symbols-outlined text-[20px]">neurology</span>
          <span>Decision Lab</span>
        </button>

        <button onclick="switchScreen('enterprise-data')" data-nav="enterprise-data" class="nav-btn w-full flex items-center gap-2.5 px-4 py-2.5 rounded-full text-[#c4c6cd] hover:bg-[#283044] hover:text-white transition-all font-grotesk font-semibold text-sm">
          <span class="material-symbols-outlined text-[20px]">database</span>
          <span>Enterprise Data</span>
        </button>

        <button onclick="switchScreen('incidents')" data-nav="incidents" class="nav-btn w-full flex items-center gap-2.5 px-4 py-2.5 rounded-full text-[#c4c6cd] hover:bg-[#283044] hover:text-white transition-all font-grotesk font-semibold text-sm">
          <span class="material-symbols-outlined text-[20px]">warning</span>
          <span>Incidents</span>
        </button>

        <button onclick="switchScreen('agent-intelligence')" data-nav="agent-intelligence" class="nav-btn w-full flex items-center gap-2.5 px-4 py-2.5 rounded-full text-[#c4c6cd] hover:bg-[#283044] hover:text-white transition-all font-grotesk font-semibold text-sm">
          <span class="material-symbols-outlined text-[20px]">smart_toy</span>
          <span>Agent Intelligence</span>
        </button>

        <button onclick="switchScreen('evaluation')" data-nav="evaluation" class="nav-btn w-full flex items-center gap-2.5 px-4 py-2.5 rounded-full text-[#c4c6cd] hover:bg-[#283044] hover:text-white transition-all font-grotesk font-semibold text-sm">
          <span class="material-symbols-outlined text-[20px]">query_stats</span>
          <span>Evaluation</span>
        </button>
      </nav>
    </div>

    <!-- Active LLM & Tenant Status Footer -->
    <div class="flex flex-col gap-2">
      <!-- LLM Provider Badge -->
      <div class="p-2.5 rounded-xl bg-[#04060a]/80 border border-white/5 flex items-center justify-between text-xs">
        <span class="flex items-center gap-1.5 text-slate-300">
          <span class="w-2 h-2 rounded-full bg-secondary-fixed" id="llm-dot"></span>
          <span id="llm-status-text" class="truncate max-w-[130px]">Ollama Checking...</span>
        </span>
        <span class="text-[10px] font-mono text-secondary-fixed font-bold uppercase">7.6B</span>
      </div>

      <!-- Autonomous Engine Status Card -->
      <div class="p-3.5 rounded-2xl bg-[#283044] flex flex-col gap-2.5 border border-white/5">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5 text-secondary-fixed">
            <span class="material-symbols-outlined text-[18px]">rocket_launch</span>
            <span class="font-grotesk text-[11px] font-bold uppercase tracking-wider">Autonomous Engine</span>
          </div>
          <span class="font-grotesk text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-fixed">99.98% Uptime</span>
        </div>
        <div class="flex items-center justify-between text-[#c4c6cd] text-xs pt-1 border-t border-white/10">
          <span class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-secondary-fixed animate-pulse"></span>
            Active Mode
          </span>
          <span class="font-grotesk text-secondary-fixed font-bold uppercase text-[11px]">Sub-12ms</span>
        </div>
      </div>

      <!-- Quick Switcher in Sidebar Footer -->
      <div class="pt-1">
        <button id="sidebar-switch-mode-btn" onclick="toggleModeSwitch()" class="w-full py-2 px-3 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-grotesk font-semibold text-slate-300 hover:text-white flex items-center justify-center gap-2 transition-all border border-white/10">
          <span class="material-symbols-outlined text-[16px]">swap_horiz</span>
          <span id="sidebar-switch-mode-text">Switch to Evaluator Console</span>
        </button>
      </div>
    </div>
  </aside>
"""

# 4. TOP HEADER BAR
header_html = """
    <!-- Top Header Bar -->
    <header class="h-16 bg-surface/85 backdrop-blur-xl border-b border-outline-variant/40 sticky top-0 z-30 px-8 flex items-center justify-between shadow-sm">
      
      <!-- Customer Header Left -->
      <div id="header-left-customer" class="flex items-center gap-4">
        <div class="flex items-center gap-2 px-4 py-1.5 rounded-full bg-white text-slate-500 border border-slate-200 shadow-sm w-80">
          <span class="material-symbols-outlined text-[18px]">search</span>
          <input class="bg-transparent border-0 outline-none w-full text-xs text-slate-800 placeholder:text-slate-400" id="cust-header-search" placeholder="Search orders or ask a question..." type="text"/>
        </div>
        <div class="hidden xl:flex items-center gap-2">
          <span class="font-grotesk text-[11px] font-bold px-3 py-1 rounded-full bg-[#bcf063] text-[#131f00] flex items-center gap-1.5 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-secondary"></span> 6 Agents Online
          </span>
          <span class="font-grotesk text-[11px] font-semibold px-3 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
            Isolated Tenant Database
          </span>
        </div>
      </div>

      <!-- Evaluator Header Left (hidden by default in customer mode) -->
      <div id="header-left-evaluator" class="hidden flex items-center gap-4">
        <div class="flex items-center gap-2 px-4 py-1.5 rounded-full bg-white text-slate-500 border border-slate-200 shadow-sm w-80">
          <span class="material-symbols-outlined text-[18px]">search</span>
          <input class="bg-transparent border-0 outline-none w-full text-xs text-slate-800 placeholder:text-slate-400" placeholder="Search telemetry or prompt agents..." type="text"/>
          <span class="font-grotesk text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">⌘K</span>
        </div>
        <div class="hidden xl:flex items-center gap-2">
          <span class="font-grotesk text-[11px] font-bold px-3 py-1 rounded-full bg-[#bcf063] text-[#131f00] flex items-center gap-1.5 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-secondary"></span> All 6 Agents Online
          </span>
          <span class="font-grotesk text-[11px] font-semibold px-3 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
            PoC Air-Gapped
          </span>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <!-- Switch View Button -->
        <button onclick="toggleModeSwitch()" id="header-switch-view-btn" class="px-3.5 py-1.5 rounded-full font-grotesk font-semibold text-xs bg-slate-900 text-secondary-fixed hover:bg-slate-800 transition-all flex items-center gap-1.5 shadow-sm">
          <span class="material-symbols-outlined text-[15px]">terminal</span>
          <span id="header-switch-view-label">Evaluator Mission Control</span>
        </button>

        <!-- Live Clock -->
        <div class="hidden md:flex flex-col text-right">
          <span class="font-grotesk text-xs font-bold text-slate-800" id="clock-utc">14:28:02 UTC</span>
          <span class="text-[11px] text-slate-500">Autonomous Core</span>
        </div>

        <!-- Auth / User Profile Pill -->
        <div class="flex items-center gap-2.5 pl-3 border-l border-slate-200">
          <div class="w-8 h-8 rounded-full bg-slate-900 text-secondary-fixed font-grotesk font-bold flex items-center justify-center text-xs shadow-sm cursor-pointer" onclick="toggleAuthModal(true)">
            <span id="user-avatar-initials">RS</span>
          </div>
          <div class="hidden lg:flex flex-col cursor-pointer" onclick="toggleAuthModal(true)">
            <span class="font-grotesk text-xs font-bold text-slate-900 leading-none" id="user-display-name">Rahul Sharma</span>
            <span class="text-[10px] text-secondary font-semibold leading-none mt-1" id="user-role-label">Customer Account</span>
          </div>
          <button onclick="handleCustomerLogout()" class="p-1 rounded-full hover:bg-slate-100 text-slate-500 hover:text-red-600 transition-colors" title="Log Out">
            <span class="material-symbols-outlined text-[18px]">logout</span>
          </button>
        </div>
      </div>
    </header>
"""

# 5. CUSTOMER SCREENS (LAYER 1)
customer_screens_html = """
      <!-- =================================================================== -->
      <!-- SCREEN: CUSTOMER HOME                                               -->
      <!-- =================================================================== -->
      <div id="screen-customer-home" class="screen-view flex flex-col gap-6">
        
        <!-- Welcome & Quick Issue Reporter Card -->
        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col gap-5">
          <div class="flex items-center justify-between">
            <div>
              <span class="text-xs font-bold text-secondary uppercase tracking-wider">Customer Support Assistant</span>
              <h2 class="font-grotesk text-2xl sm:text-3xl font-extrabold text-slate-950 mt-1">
                Welcome back, <span id="welcome-cust-name">Rahul</span>. How can ResolveX help you today?
              </h2>
              <p class="text-xs text-slate-600 mt-1">
                Type your issue below in plain English. ResolveX will cross-reference your orders, verify payments, and resolve it autonomously.
              </p>
            </div>
            <div id="guest-reset-badge" class="hidden">
              <button onclick="handleResetDemo()" class="px-3 py-1.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold hover:bg-amber-100 flex items-center gap-1.5 transition-colors">
                <span class="material-symbols-outlined text-[16px]">refresh</span> Reset Demo
              </button>
            </div>
          </div>

          <div class="flex items-center gap-2 p-1.5 rounded-2xl bg-slate-50 border border-slate-300 shadow-inner">
            <span class="material-symbols-outlined text-slate-400 pl-3">search</span>
            <input type="text" id="cust-home-input" placeholder="e.g. ₹2,499 was deducted from my account but order failed (Gateway Timeout 504)..." class="bg-transparent border-0 outline-none w-full text-xs text-slate-800 placeholder:text-slate-400 py-2.5"/>
            <button onclick="submitCustomerIssueFromHome()" class="px-6 py-2.5 rounded-xl bg-primary text-secondary-fixed font-grotesk font-bold text-xs hover:bg-primary/90 transition-all shadow-md shrink-0 flex items-center gap-1.5">
              <span>Ask ResolveX</span>
              <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
            </button>
          </div>

          <!-- Predefined Demonstration Scenarios Chips -->
          <div class="flex flex-wrap items-center gap-2 pt-1">
            <span class="text-[11px] font-semibold text-slate-500">Popular issues:</span>
            <button onclick="applyPromptChip('₹2,499 was deducted from my account but my order failed (Gateway Timeout 504).')" class="px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs transition-colors">
              💳 Payment Deducted, Order Failed
            </button>
            <button onclick="applyPromptChip('I want a refund for my RedBus booking RB-10291.')" class="px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs transition-colors">
              🚌 RedBus Booking Cancellation
            </button>
            <button onclick="applyPromptChip('I received the wrong product for Amazon order ORD-8801.')" class="px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs transition-colors">
              📦 Wrong Item Delivered (Amazon)
            </button>
            <button onclick="applyPromptChip('Customer submitted second claim for ₹2,499 on Order #ORD-5502.')" class="px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs transition-colors">
              🔄 Track Existing Refund (Duplicate Guard)
            </button>
          </div>
        </div>

        <!-- 4-Card Quick Metrics Strip -->
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <span class="text-xs font-semibold text-slate-500">Active Bookings & Orders</span>
              <div class="font-grotesk text-2xl font-bold text-slate-900 mt-1" id="cust-stat-orders">12</div>
            </div>
            <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <span class="material-symbols-outlined">shopping_bag</span>
            </div>
          </div>

          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <span class="text-xs font-semibold text-slate-500">Open Inquiries</span>
              <div class="font-grotesk text-2xl font-bold text-slate-900 mt-1" id="cust-stat-cases">1</div>
            </div>
            <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <span class="material-symbols-outlined">receipt_long</span>
            </div>
          </div>

          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <span class="text-xs font-semibold text-slate-500">Reconciled Refunds</span>
              <div class="font-grotesk text-2xl font-bold text-emerald-600 mt-1" id="cust-stat-refunds">₹4,998</div>
            </div>
            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <span class="material-symbols-outlined">verified</span>
            </div>
          </div>

          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <span class="text-xs font-semibold text-slate-500">Autonomous SLA</span>
              <div class="font-grotesk text-2xl font-bold text-secondary mt-1">&lt; 250ms</div>
            </div>
            <div class="w-10 h-10 rounded-xl bg-slate-900 text-secondary-fixed flex items-center justify-center">
              <span class="material-symbols-outlined">bolt</span>
            </div>
          </div>
        </div>

        <!-- 2-Column Section: Orders & Activity Timeline -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          <!-- Column 1: Recent Orders & Bookings with Provider Context -->
          <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col gap-4">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-secondary text-[20px]">shopping_bag</span>
                <h3 class="font-grotesk font-bold text-slate-900 text-base">My Recent Orders & Bookings</h3>
              </div>
              <button onclick="switchScreen('customer-orders')" class="text-xs font-semibold text-secondary hover:underline">
                View All &rarr;
              </button>
            </div>

            <div id="cust-orders-list" class="flex flex-col gap-3">
              <!-- Populated dynamically via JS -->
              <div class="text-xs text-slate-500 py-4 text-center">Loading customer orders...</div>
            </div>
          </div>

          <!-- Column 2: Recent Activity Timeline -->
          <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col gap-4">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-secondary text-[20px]">timeline</span>
                <h3 class="font-grotesk font-bold text-slate-900 text-base">Resolution Activity & Cases</h3>
              </div>
              <button onclick="switchScreen('customer-requests')" class="text-xs font-semibold text-secondary hover:underline">
                View History &rarr;
              </button>
            </div>

            <div id="cust-timeline-list" class="flex flex-col gap-3">
              <!-- Populated dynamically via JS -->
              <div class="text-xs text-slate-500 py-4 text-center">Loading activity timeline...</div>
            </div>
          </div>

        </div>
      </div>

      <!-- =================================================================== -->
      <!-- SCREEN: MY ORDERS & BOOKINGS                                        -->
      <!-- =================================================================== -->
      <div id="screen-customer-orders" class="screen-view hidden flex flex-col gap-6">
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col gap-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <h2 class="font-grotesk text-2xl font-extrabold text-slate-950">My Orders & Bookings</h2>
              <p class="text-xs text-slate-500 mt-1">
                Real synthetic orders across connected providers (RedBus, Amazon, Flipkart, MakeMyTrip, Swiggy).
              </p>
            </div>
            
            <div class="flex items-center gap-2">
              <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs">
                <span class="material-symbols-outlined text-[16px] text-slate-400">search</span>
                <input type="text" id="order-filter-search" oninput="filterCustomerOrders()" placeholder="Search orders..." class="bg-transparent border-0 outline-none w-40 text-xs text-slate-800"/>
              </div>
            </div>
          </div>

          <!-- Provider Filter Tabs -->
          <div class="flex flex-wrap items-center gap-2">
            <button onclick="setOrderCategoryFilter('ALL')" class="order-filter-btn px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-900 text-secondary-fixed shadow-sm" data-cat="ALL">All Providers</button>
            <button onclick="setOrderCategoryFilter('RedBus')" class="order-filter-btn px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200" data-cat="RedBus">RedBus (Buses)</button>
            <button onclick="setOrderCategoryFilter('MakeMyTrip')" class="order-filter-btn px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200" data-cat="MakeMyTrip">MakeMyTrip (Hotels)</button>
            <button onclick="setOrderCategoryFilter('Amazon')" class="order-filter-btn px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200" data-cat="Amazon">Amazon (Shopping)</button>
            <button onclick="setOrderCategoryFilter('Flipkart')" class="order-filter-btn px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200" data-cat="Flipkart">Flipkart</button>
            <button onclick="setOrderCategoryFilter('Swiggy')" class="order-filter-btn px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200" data-cat="Swiggy">Swiggy (Food)</button>
          </div>

          <!-- Orders List -->
          <div id="full-orders-list" class="flex flex-col gap-3 pt-2">
            <div class="text-xs text-slate-500 py-8 text-center">Loading orders...</div>
          </div>
        </div>
      </div>

      <!-- =================================================================== -->
      <!-- SCREEN: RECENT REQUESTS                                             -->
      <!-- =================================================================== -->
      <div id="screen-customer-requests" class="screen-view hidden flex flex-col gap-6">
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col gap-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <h2 class="font-grotesk text-2xl font-extrabold text-slate-950">Recent Requests & Case History</h2>
              <p class="text-xs text-slate-500 mt-1">
                Real-time status of your autonomous resolution dockets, bank refund tracking, and policy citations.
              </p>
            </div>
            <button onclick="loadCustomerRequestsData()" class="px-4 py-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors">
              <span class="material-symbols-outlined text-[16px]">refresh</span> Refresh Status
            </button>
          </div>

          <!-- Requests Stats Strip -->
          <div class="grid grid-cols-1 sm:grid-cols-4 gap-4 py-2">
            <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col">
              <span class="text-xs text-slate-500 font-semibold">Total Support Cases</span>
              <span class="font-grotesk text-xl font-bold text-slate-900 mt-1" id="req-stat-total">3</span>
            </div>
            <div class="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 flex flex-col">
              <span class="text-xs text-emerald-700 font-semibold">Autonomously Resolved</span>
              <span class="font-grotesk text-xl font-bold text-emerald-800 mt-1" id="req-stat-resolved">2</span>
            </div>
            <div class="p-4 rounded-2xl bg-blue-50 border border-blue-200 flex flex-col">
              <span class="text-xs text-blue-700 font-semibold">Bank Settlement In Progress</span>
              <span class="font-grotesk text-xl font-bold text-blue-800 mt-1" id="req-stat-bank">1</span>
            </div>
            <div class="p-4 rounded-2xl bg-amber-50 border border-amber-200 flex flex-col">
              <span class="text-xs text-amber-700 font-semibold">Escalated to SecOps</span>
              <span class="font-grotesk text-xl font-bold text-amber-800 mt-1" id="req-stat-escalated">0</span>
            </div>
          </div>

          <!-- Dynamic Requests & Refunds List -->
          <div id="full-requests-list" class="flex flex-col gap-3 pt-2">
            <div class="text-xs text-slate-500 py-8 text-center">Loading recent requests and refunds...</div>
          </div>
        </div>
      </div>

      <!-- =================================================================== -->
      <!-- SCREEN: HELP & SUPPORT                                              -->
      <!-- =================================================================== -->
      <div id="screen-customer-help" class="screen-view hidden flex flex-col gap-6">
        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col gap-6">
          <div>
            <span class="text-xs font-bold text-secondary uppercase tracking-wider">Help & Support Center</span>
            <h2 class="font-grotesk text-2xl sm:text-3xl font-extrabold text-slate-950 mt-1">
              How can we assist you today?
            </h2>
            <p class="text-xs text-slate-600 mt-1">
              ResolveX resolves common customer issues autonomously. Choose a topic below or speak directly to the AI assistant.
            </p>
          </div>

          <!-- 4 Actionable Category Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div onclick="applyPromptChip('₹2,499 was deducted from my account but my order failed (Gateway Timeout 504).')" class="p-5 rounded-2xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer transition-all flex items-start gap-4">
              <div class="w-10 h-10 rounded-xl bg-slate-900 text-secondary-fixed flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined">credit_card_off</span>
              </div>
              <div class="flex flex-col gap-1">
                <h4 class="font-grotesk font-bold text-sm text-slate-900">Failed Payment & Gateway Timeouts (PG 504)</h4>
                <p class="text-xs text-slate-600">
                  Money debited but order not created? ResolveX checks Razorpay/PayU logs and credits back an instant autonomous refund under POL-REF-01.
                </p>
                <span class="text-[11px] font-semibold text-secondary mt-1 flex items-center gap-1">
                  Start Resolution &rarr;
                </span>
              </div>
            </div>

            <div onclick="applyPromptChip('I want a refund for my RedBus booking RB-10291.')" class="p-5 rounded-2xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer transition-all flex items-start gap-4">
              <div class="w-10 h-10 rounded-xl bg-slate-900 text-secondary-fixed flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined">directions_bus</span>
              </div>
              <div class="flex flex-col gap-1">
                <h4 class="font-grotesk font-bold text-sm text-slate-900">Bus & Flight Ticket Cancellations</h4>
                <p class="text-xs text-slate-600">
                  Cancellations evaluated against provider cancellation windows (RedBus POL-RB-01/02 and MakeMyTrip policies) with zero human delays.
                </p>
                <span class="text-[11px] font-semibold text-secondary mt-1 flex items-center gap-1">
                  Check Cancellation &rarr;
                </span>
              </div>
            </div>

            <div onclick="applyPromptChip('I received the wrong product for Amazon order ORD-8801.')" class="p-5 rounded-2xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer transition-all flex items-start gap-4">
              <div class="w-10 h-10 rounded-xl bg-slate-900 text-secondary-fixed flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined">package_2</span>
              </div>
              <div class="flex flex-col gap-1">
                <h4 class="font-grotesk font-bold text-sm text-slate-900">Wrong or Damaged Product Delivered</h4>
                <p class="text-xs text-slate-600">
                  Doorstep reverse pickup scheduled automatically with carrier tracking for wrong items or damaged shipments within 7 days.
                </p>
                <span class="text-[11px] font-semibold text-secondary mt-1 flex items-center gap-1">
                  Schedule Pickup &rarr;
                </span>
              </div>
            </div>

            <div onclick="applyPromptChip('I was charged twice for my subscription order ORD-9102.')" class="p-5 rounded-2xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer transition-all flex items-start gap-4">
              <div class="w-10 h-10 rounded-xl bg-slate-900 text-secondary-fixed flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined">autorenew</span>
              </div>
              <div class="flex flex-col gap-1">
                <h4 class="font-grotesk font-bold text-sm text-slate-900">Subscription & Duplicate Charges</h4>
                <p class="text-xs text-slate-600">
                  Identifies erroneous recurring debits or duplicate charges after cancellation, reversing charges under subscription policy POL-SUB-01.
                </p>
                <span class="text-[11px] font-semibold text-secondary mt-1 flex items-center gap-1">
                  Dispute Charge &rarr;
                </span>
              </div>
            </div>
          </div>

          <!-- How ResolveX Works Card -->
          <div class="p-6 rounded-2xl bg-[#1c1f24] text-white flex flex-col gap-3 border border-white/10">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary-fixed text-[20px]">smart_toy</span>
              <h4 class="font-grotesk font-bold text-sm text-white">How ResolveX Works Under the Hood</h4>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed">
              ResolveX does not use canned responses. When you report an issue, our <b>6 autonomous agents</b> (Planner, Research, Critic, Executor, Business Automation, and Software Development) collaborate in a LangGraph StateGraph. The system verifies payment telemetry, retrieves enterprise policies via RAG, enforces strict safety guardrails, and executes genuine bank disbursements.
            </p>
          </div>

          <!-- Human Escalation Notice -->
          <div class="p-6 rounded-2xl bg-amber-50 border border-amber-200 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="flex items-start gap-3">
              <span class="material-symbols-outlined text-amber-600 text-[24px]">contact_support</span>
              <div class="flex flex-col">
                <h4 class="font-grotesk font-bold text-sm text-amber-950">Need Direct Human Support?</h4>
                <p class="text-xs text-amber-800">
                  High-value cases exceeding ₹25,000 or policy anomalies are automatically forwarded to our Senior Operations Lead with a 2-4 hour turnaround.
                </p>
              </div>
            </div>
            <button onclick="toggleChatDrawer(true)" class="px-5 py-2.5 rounded-full bg-slate-900 text-secondary-fixed text-xs font-grotesk font-bold shrink-0 hover:bg-slate-800 transition-all">
              Start New Request
            </button>
          </div>
        </div>
      </div>

      <!-- =================================================================== -->
      <!-- SCREEN: ACCOUNT & SESSION                                           -->
      <!-- =================================================================== -->
      <div id="screen-customer-account" class="screen-view hidden flex flex-col gap-6">
        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col gap-6">
          <div>
            <h2 class="font-grotesk text-2xl font-extrabold text-slate-950">Account & Session Details</h2>
            <p class="text-xs text-slate-500 mt-1">
              Customer credentials, trust telemetry, and multi-tenant isolated database environment.
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Profile Card -->
            <div class="p-6 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col gap-4">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-2xl bg-slate-900 text-secondary-fixed font-grotesk font-bold flex items-center justify-center text-lg" id="acc-avatar">
                  RS
                </div>
                <div>
                  <h4 class="font-grotesk font-bold text-base text-slate-900" id="acc-name">Rahul Sharma</h4>
                  <span class="text-xs text-slate-500" id="acc-email">rahul.sharma@example.in</span>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-3 pt-2 border-t border-slate-200 text-xs">
                <div>
                  <span class="text-slate-500">Customer ID</span>
                  <div class="font-mono font-semibold text-slate-800 mt-0.5" id="acc-cust-id">CUST-101</div>
                </div>
                <div>
                  <span class="text-slate-500">Trust Score</span>
                  <div class="font-semibold text-emerald-600 mt-0.5" id="acc-trust">96 / 100 (Tier 1)</div>
                </div>
                <div>
                  <span class="text-slate-500">Phone</span>
                  <div class="font-semibold text-slate-800 mt-0.5">+91-9876543210</div>
                </div>
                <div>
                  <span class="text-slate-500">Region</span>
                  <div class="font-semibold text-slate-800 mt-0.5">Mumbai, MH</div>
                </div>
              </div>
            </div>

            <!-- Session & Environment Card -->
            <div class="p-6 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col gap-4">
              <h4 class="font-grotesk font-bold text-sm text-slate-900">Tenant Environment & Isolation</h4>
              
              <div class="flex flex-col gap-2.5 text-xs">
                <div class="flex items-center justify-between">
                  <span class="text-slate-500">User ID</span>
                  <span class="font-mono text-slate-800 font-semibold" id="acc-user-id">USER-CUST-DEMO</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-slate-500">Session Mode</span>
                  <span class="px-2 py-0.5 rounded-full bg-slate-200 text-slate-800 font-semibold text-[11px]" id="acc-session-type">Authenticated Customer</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-slate-500">Database Scope</span>
                  <span class="text-emerald-700 font-semibold">Isolated SQLite Tenant Store</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-slate-500">LLM Provider</span>
                  <span class="font-semibold text-slate-800" id="acc-llm-label">Ollama (qwen2.5-coder:7b)</span>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-3 pt-3 border-t border-slate-200">
                <button onclick="handleCustomerLogout()" class="px-4 py-2 rounded-xl bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-semibold transition-colors">
                  Sign Out
                </button>
                <button onclick="toggleModeSwitch()" class="px-4 py-2 rounded-xl bg-primary text-secondary-fixed text-xs font-semibold transition-all">
                  Switch to Evaluator Console
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
"""

# 6. EXTRACT TECH SCREENS AND MODALS
s_start = orig.find('<div id="screen-mission-control"')
s_end = orig.find('</main>')
tech_screens_html = orig[s_start:s_end]
if """          <!-- Predefined Scenarios Quick-Picks -->
          <div class="flex flex-wrap items-center gap-2">
            <span class="font-grotesk text-[11px] font-bold text-slate-400 uppercase tracking-wider pr-1">Predefined Scenarios:</span>
            <button onclick="previewScenario('pg-504')" data-scen="pg-504" class="scen-pill px-4 py-1.5 rounded-full text-xs font-grotesk font-bold bg-secondary-fixed text-on-secondary-fixed flex items-center gap-1.5 shadow-sm">
              <span class="w-2 h-2 rounded-full bg-secondary"></span> PG 504 Auto-Refund
            </button>
            <button onclick="previewScenario('duplicate-claim')" data-scen="duplicate-claim" class="scen-pill px-4 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Duplicate Claim Blocked
            </button>
            <button onclick="previewScenario('tor-escalate')" data-scen="tor-escalate" class="scen-pill px-4 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> High-Risk Tor Escalation
            </button>
            <button onclick="previewScenario('pg-spike')" data-scen="pg-spike" class="scen-pill px-4 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Systemic PG Spike (1.4k/s)
            </button>
          </div>""" in tech_screens_html:
    tech_screens_html = tech_screens_html.replace("""          <!-- Predefined Scenarios Quick-Picks -->
          <div class="flex flex-wrap items-center gap-2">
            <span class="font-grotesk text-[11px] font-bold text-slate-400 uppercase tracking-wider pr-1">Predefined Scenarios:</span>
            <button onclick="previewScenario('pg-504')" data-scen="pg-504" class="scen-pill px-4 py-1.5 rounded-full text-xs font-grotesk font-bold bg-secondary-fixed text-on-secondary-fixed flex items-center gap-1.5 shadow-sm">
              <span class="w-2 h-2 rounded-full bg-secondary"></span> PG 504 Auto-Refund
            </button>
            <button onclick="previewScenario('duplicate-claim')" data-scen="duplicate-claim" class="scen-pill px-4 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Duplicate Claim Blocked
            </button>
            <button onclick="previewScenario('tor-escalate')" data-scen="tor-escalate" class="scen-pill px-4 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> High-Risk Tor Escalation
            </button>
            <button onclick="previewScenario('pg-spike')" data-scen="pg-spike" class="scen-pill px-4 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Systemic PG Spike (1.4k/s)
            </button>
          </div>""", """          <!-- Predefined Scenarios Quick-Picks (10 Multi-Domain Scenarios) -->
          <div class="flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <span class="font-grotesk text-[11px] font-bold text-slate-400 uppercase tracking-wider">Multi-Domain Evaluation Scenarios (6+ Industry Domains):</span>
              <span class="text-[10px] text-slate-400 font-mono">10 Scenarios Seeded</span>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <button onclick="previewScenario('pg-504')" data-scen="pg-504" class="scen-pill px-3.5 py-1.5 rounded-full text-xs font-grotesk font-bold bg-secondary-fixed text-on-secondary-fixed flex items-center gap-1.5 shadow-sm">
                <span class="w-2 h-2 rounded-full bg-secondary"></span> 💳 PG 504 Auto-Refund
              </button>
              <button onclick="previewScenario('duplicate-claim')" data-scen="duplicate-claim" class="scen-pill px-3.5 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> ↺ Duplicate Block (Replan)
              </button>
              <button onclick="previewScenario('tor-escalate')" data-scen="tor-escalate" class="scen-pill px-3.5 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> 🛡 Tor Escalation (>₹25k)
              </button>
              <button onclick="previewScenario('pg-spike')" data-scen="pg-spike" class="scen-pill px-3.5 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> ⚡ Systemic Spike (1.4k/s)
              </button>
              <button onclick="previewScenario('travel-cancel')" data-scen="travel-cancel" class="scen-pill px-3.5 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> 🚌 Travel Cancel (RedBus)
              </button>
              <button onclick="previewScenario('travel-ineligible')" data-scen="travel-ineligible" class="scen-pill px-3.5 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> ⚠️ Ineligible Cancel (<4h)
              </button>
              <button onclick="previewScenario('wrong-product')" data-scen="wrong-product" class="scen-pill px-3.5 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> 📦 Wrong Product (Amazon)
              </button>
              <button onclick="previewScenario('damaged-product')" data-scen="damaged-product" class="scen-pill px-3.5 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> 🖥 Damaged Item (Flipkart)
              </button>
              <button onclick="previewScenario('food-spill')" data-scen="food-spill" class="scen-pill px-3.5 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> 🍲 Food Spillage (Swiggy)
              </button>
              <button onclick="previewScenario('subscription-renewal')" data-scen="subscription-renewal" class="scen-pill px-3.5 py-1.5 rounded-full text-xs font-grotesk font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> 🔄 Prime Auto-Renewal
              </button>
            </div>
          </div>""")


m_start = orig.find('id="auth-modal"')
m_tag_start = orig.rfind('<div', 0, m_start)
m_end = orig.find('<script', m_start)
modals_html = orig[m_tag_start:m_end]

# 7. SLIDE-OUT CHATBOT DRAWER HTML
drawer_html = """
  <!-- ========================================================================= -->
  <!-- SLIDE-OVER CHAT DRAWER (POLISHED CUSTOMER CONVERSATION EXPERIENCE)        -->
  <!-- ========================================================================= -->
  <div id="chat-drawer" class="hidden fixed inset-0 z-50 chat-drawer-backdrop flex justify-end">
    <div class="bg-white w-full max-w-xl h-full shadow-2xl flex flex-col justify-between border-l border-slate-200">
      
      <!-- Drawer Header -->
      <div class="h-16 px-6 bg-white border-b border-slate-200 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-primary text-secondary-fixed flex items-center justify-center font-bold text-sm shadow-sm">
            ⚡
          </div>
          <div>
            <h3 class="font-grotesk font-bold text-sm text-slate-900 leading-none">ResolveX Assistant</h3>
            <span class="text-[10px] text-emerald-600 font-semibold flex items-center gap-1 mt-0.5">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Online • 6 Agents Active
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="clearCurrentConversation()" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition-colors" title="New Conversation">
            <span class="material-symbols-outlined text-[18px]">add_comment</span>
          </button>
          <button onclick="toggleChatDrawer(false)" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition-colors" title="Close Drawer">
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
      </div>

      <!-- Chat Messages Container -->
      <div id="drawer-messages" class="flex-1 overflow-y-auto p-6 flex flex-col gap-4 custom-scroll bg-slate-50">
        <!-- Initial Welcome Message -->
        <div class="flex items-start gap-3 max-w-lg">
          <div class="w-8 h-8 rounded-xl bg-primary text-secondary-fixed flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 shadow-sm">
            ⚡
          </div>
          <div class="flex flex-col gap-1.5 bg-white p-4 rounded-2xl rounded-tl-sm border border-slate-200 shadow-sm text-xs text-slate-800 leading-relaxed">
            <div class="flex items-center justify-between">
              <span class="font-grotesk font-bold text-slate-900">ResolveX Assistant</span>
              <span class="text-[10px] text-slate-400">Just now</span>
            </div>
            <p>
              Hi! I'm <b>ResolveX</b>, your autonomous customer resolution engine.
            </p>
            <p class="text-slate-600">
              You can ask me about refunds, cancellations, failed payments, orders, bookings, damaged items, or anything else you need help with.
            </p>
          </div>
        </div>
      </div>

      <!-- Suggestion Chips -->
      <div class="px-6 py-2 bg-slate-50 border-t border-slate-200/60 flex items-center gap-2 overflow-x-auto custom-scroll">
        <button onclick="applyDrawerChip('₹2,499 was deducted from my account but my order failed (Gateway Timeout 504).')" class="px-3 py-1 rounded-full bg-white border border-slate-200 text-[11px] text-slate-700 hover:bg-slate-100 shrink-0 shadow-2xs">
          💳 PG Timeout 504 (₹2,499)
        </button>
        <button onclick="applyDrawerChip('I want a refund for my RedBus booking RB-10291.')" class="px-3 py-1 rounded-full bg-white border border-slate-200 text-[11px] text-slate-700 hover:bg-slate-100 shrink-0 shadow-2xs">
          🚌 RedBus (RB-10291)
        </button>
        <button onclick="applyDrawerChip('I received the wrong product for Amazon order ORD-8801.')" class="px-3 py-1 rounded-full bg-white border border-slate-200 text-[11px] text-slate-700 hover:bg-slate-100 shrink-0 shadow-2xs">
          📦 Amazon Wrong Item
        </button>
        <button onclick="applyDrawerChip('Customer submitted second claim for ₹2,499 on Order #ORD-5502.')" class="px-3 py-1 rounded-full bg-white border border-slate-200 text-[11px] text-slate-700 hover:bg-slate-100 shrink-0 shadow-2xs">
          🔄 Duplicate Check
        </button>
        <button onclick="applyDrawerChip('Hello')" class="px-3 py-1 rounded-full bg-white border border-slate-200 text-[11px] text-slate-700 hover:bg-slate-100 shrink-0 shadow-2xs">
          👋 Say Hello
        </button>
      </div>

      <!-- Input Bar -->
      <div class="p-4 bg-white border-t border-slate-200 flex items-center gap-2">
        <input type="text" id="drawer-input" onkeydown="handleDrawerKeyDown(event)" placeholder="Type your message or order ID..." class="flex-1 px-4 py-2.5 rounded-full border border-slate-300 text-xs focus:outline-none focus:border-primary"/>
        <button onclick="sendDrawerMessage()" id="drawer-send-btn" class="w-10 h-10 rounded-full bg-primary text-secondary-fixed flex items-center justify-center hover:bg-primary/90 transition-all shadow-md shrink-0">
          <span class="material-symbols-outlined text-[18px]">send</span>
        </button>
      </div>

    </div>
  </div>

  <!-- Floating Action Button: [ Ask ResolveX ] -->
  <div id="floating-chat-btn-container" class="fixed bottom-6 right-6 z-40">
    <button onclick="toggleChatDrawer(true)" class="px-5 py-3.5 rounded-full bg-primary text-secondary-fixed font-grotesk font-bold text-sm shadow-xl shadow-black/30 hover:bg-primary/90 transition-all flex items-center gap-2.5">
      <span class="material-symbols-outlined text-[20px]">chat</span>
      <span>Ask ResolveX</span>
    </button>
  </div>
"""

# 8. SCRIPT CODE
sc_start = orig.find('<script', orig.find('</main>'))
sc_end = orig.rfind('</script>')
orig_script_tag = orig[sc_start:sc_end]
orig_js = orig_script_tag[orig_script_tag.find('>')+1:]

customer_js = """

    const scenarioDataExtra = {
      'travel-cancel': {
        title: "Scenario: Travel Cancellation (RedBus >24h)",
        desc: "Customer requests cancellation of RedBus Volvo ticket 48 hours prior to departure. Eligible for 100% autonomous refund under Policy POL-RB-01.",
        tag: "Autonomous Travel Refund",
        text: "Please cancel my RedBus ticket for tomorrow morning (Order #ORD-9001). Need full refund under travel cancellation policy."
      },
      'travel-ineligible': {
        title: "Scenario: Travel Cancellation (RedBus <4h Ineligible)",
        desc: "Customer requests refund after bus has departed or within 4 hours. Ineligible for automatic refund under Policy POL-RB-02; safely escalates for concession review.",
        tag: "Policy Restriction & Concession",
        text: "Bus has already left, but I missed it due to traffic. Please refund my ticket #ORD-9002 immediately."
      },
      'wrong-product': {
        title: "Scenario: Wrong Product Received (Amazon)",
        desc: "Customer received wireless mouse instead of Sony WH-1000XM5 headphones on Order #ORD-9004. Autonomous doorstep replacement scheduled under Policy POL-AMZ-WRONG.",
        tag: "Doorstep Pickup & Replacement",
        text: "I received an optical mouse instead of Sony WH-1000XM5 wireless headphones on Order #ORD-9004. Please dispatch correct replacement."
      },
      'damaged-product': {
        title: "Scenario: Damaged In Transit (Flipkart)",
        desc: "Customer received LG 27-inch 4K monitor with cracked display panel on Order #ORD-9005. Free doorstep replacement scheduled under Policy POL-FK-DAMAGED.",
        tag: "Damaged Item Replacement",
        text: "My LG 27-inch 4K monitor arrived with a completely shattered display panel on Order #ORD-9005. Requesting immediate replacement."
      },
      'food-spill': {
        title: "Scenario: Food Delivery Spillage (Swiggy)",
        desc: "Customer received food delivery with container spilled inside packaging on Order #ORD-9006. Instant credit issued to Swiggy Money wallet under Policy POL-SWIGGY-SPILL.",
        tag: "Instant Wallet Credit",
        text: "Food delivery from Swiggy arrived damaged with gravy spilled completely inside the bag on Order #ORD-9006."
      },
      'subscription-renewal': {
        title: "Scenario: Unused Subscription Renewal",
        desc: "Customer disputes annual renewal of ₹1,499 auto-debited without usage on Order #ORD-9007. Cancellation and full refund executed under Policy POL-SUB-01.",
        tag: "Prorated Dispute Refund",
        text: "My Amazon Prime annual renewal of ₹1,499 was auto-debited without notification. I have not used benefits, please cancel and refund."
      }
    };
    Object.assign(scenarioData, scenarioDataExtra);

    // Hybrid Multi-Layer UI Controller
    let currentAppMode = 'customer'; // 'customer' or 'evaluator'
    let currentUserSession = null;
    let customerOrdersCache = [];

    function showLandingView() {
      document.getElementById('view-landing').classList.remove('hidden');
      document.getElementById('app-chassis').classList.add('hidden');
    }

    function showAppChassis() {
      document.getElementById('view-landing').classList.add('hidden');
      document.getElementById('app-chassis').classList.remove('hidden');
    }

    function setAuthTab(tab) {
      const tabCust = document.getElementById('tab-btn-customer');
      const tabEval = document.getElementById('tab-btn-evaluator');
      const pnlCust = document.getElementById('auth-panel-customer');
      const pnlEval = document.getElementById('auth-panel-evaluator');
      if (!tabCust || !tabEval || !pnlCust || !pnlEval) return;

      if (tab === 'evaluator') {
        tabEval.className = "flex-1 py-2.5 text-xs font-grotesk font-bold rounded-xl transition-all bg-white text-slate-900 shadow-sm flex items-center justify-center gap-1.5";
        tabCust.className = "flex-1 py-2.5 text-xs font-grotesk font-bold rounded-xl transition-all text-slate-500 hover:text-slate-800 flex items-center justify-center gap-1.5";
        pnlEval.classList.remove('hidden');
        pnlCust.classList.add('hidden');
        const err = document.getElementById('evaluator-login-error');
        if (err) err.classList.add('hidden');
      } else {
        tabCust.className = "flex-1 py-2.5 text-xs font-grotesk font-bold rounded-xl transition-all bg-white text-slate-900 shadow-sm flex items-center justify-center gap-1.5";
        tabEval.className = "flex-1 py-2.5 text-xs font-grotesk font-bold rounded-xl transition-all text-slate-500 hover:text-slate-800 flex items-center justify-center gap-1.5";
        pnlCust.classList.remove('hidden');
        pnlEval.classList.add('hidden');
        const err = document.getElementById('customer-login-error');
        if (err) err.classList.add('hidden');
      }
    }

    function scrollToAuth(mode) {
      if (mode === 'evaluator') {
        setAuthTab('evaluator');
      } else {
        setAuthTab('customer');
      }
      document.getElementById('auth-section').scrollIntoView({ behavior: 'smooth' });
      const targetInput = mode === 'evaluator' ? document.getElementById('eval-ident') : document.getElementById('landing-ident');
      if (targetInput) targetInput.focus();
    }

    function fillDemoCredentials(u, p) {
      setAuthTab('customer');
      const idInp = document.getElementById('landing-ident');
      const pwInp = document.getElementById('landing-pwd');
      if (idInp) idInp.value = u;
      if (pwInp) pwInp.value = p;
    }

    async function startGuestSession() {
      try {
        const resp = await fetch('/api/auth/guest', { method: 'POST' });
        const data = await resp.json();
        if (data.status === 'success') {
          currentUserSession = data.user;
          localStorage.setItem('resolvex_user', JSON.stringify(data.user));
          switchToCustomerMode();
        }
      } catch (e) {
        console.error("Guest session error", e);
      }
    }

    async function handleCustomerLogin(e) {
      if (e) e.preventDefault();
      const ident = document.getElementById('landing-ident').value.trim();
      const pwd = document.getElementById('landing-pwd').value.trim();
      const errBox = document.getElementById('customer-login-error');
      if (errBox) errBox.classList.add('hidden');

      try {
        const resp = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username_or_email: ident, password: pwd })
        });
        const data = await resp.json();
        if (data.status === 'success') {
          currentUserSession = data.user;
          localStorage.setItem('resolvex_user', JSON.stringify(data.user));
          if (data.user.role === 'EVALUATOR' || data.user.role === 'STAFF_ARCHITECT') {
            switchToEvaluatorMode();
          } else {
            switchToCustomerMode();
          }
        } else {
          if (errBox) {
            errBox.innerText = data.message || "Invalid credentials.";
            errBox.classList.remove('hidden');
          } else {
            alert(data.message || "Invalid credentials.");
          }
        }
      } catch (err) {
        console.error("Customer login error", err);
        if (errBox) {
          errBox.innerText = "Network error communicating with auth service.";
          errBox.classList.remove('hidden');
        }
      }
    }

    async function handleEvaluatorLogin(e) {
      if (e) e.preventDefault();
      const ident = document.getElementById('eval-ident').value.trim();
      const pwd = document.getElementById('eval-pwd').value.trim();
      const errBox = document.getElementById('evaluator-login-error');
      if (errBox) errBox.classList.add('hidden');

      try {
        const resp = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username_or_email: ident, password: pwd })
        });
        const data = await resp.json();
        if (data.status === 'success' && (data.user.role === 'EVALUATOR' || data.user.role === 'STAFF_ARCHITECT' || data.user.role === 'OPERATOR')) {
          currentUserSession = data.user;
          localStorage.setItem('resolvex_user', JSON.stringify(data.user));
          switchToEvaluatorMode();
        } else {
          const msg = (data.status === 'success') ? "Account does not have Evaluator/Architect privileges." : (data.message || "Invalid evaluator credentials.");
          if (errBox) {
            errBox.innerText = msg;
            errBox.classList.remove('hidden');
          } else {
            alert(msg);
          }
        }
      } catch (err) {
        console.error("Evaluator login error", err);
        if (errBox) {
          errBox.innerText = "Network error communicating with auth service.";
          errBox.classList.remove('hidden');
        }
      }
    }

    function handleCustomerLogout() {
      const userToLogout = currentUserSession;
      localStorage.removeItem('resolvex_user');
      currentUserSession = null;
      customerOrdersCache = [];

      // Clear drawer messages to fresh initial welcome bubble
      const drawerMsg = document.getElementById('drawer-messages');
      if (drawerMsg) {
        drawerMsg.innerHTML = `
          <div class="flex items-start gap-3 max-w-lg">
            <div class="w-8 h-8 rounded-xl bg-primary text-secondary-fixed flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 shadow-sm">
              ⚡
            </div>
            <div class="bg-white p-4 rounded-2xl rounded-tl-sm border border-slate-200 shadow-sm text-xs text-slate-800 leading-relaxed">
              Hello! I am your ResolveX Autonomous Assistant. How can I help you today?
            </div>
          </div>
        `;
      }

      // Clear DOM containers so User B never sees User A's data
      const resetContainers = ['cust-orders-list', 'full-orders-list', 'full-requests-list', 'cust-timeline-list'];
      resetContainers.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '<div class="p-8 text-center text-xs text-slate-400">Loading your account records...</div>';
      });

      // Clear input fields
      const inputs = ['landing-ident', 'landing-pwd', 'cust-home-input', 'drawer-input'];
      inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });

      // Reset displayed greeting and username
      const welcomeEl = document.getElementById('welcome-cust-name');
      if (welcomeEl) welcomeEl.innerText = 'Customer';
      const sideName = document.getElementById('sidebar-user-name');
      if (sideName) sideName.innerText = 'Customer';

      if (userToLogout && userToLogout.session_id) {
        fetch('/api/auth/logout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: userToLogout.session_id, user_id: userToLogout.user_id })
        }).catch(() => {});
      } else {
        fetch('/api/auth/logout', { method: 'POST' }).catch(() => {});
      }

      showLandingView();
    }

    async function handleResetDemo() {
      if (!currentUserSession || !currentUserSession.user_id) return;
      if (!currentUserSession.user_id.startsWith('GUEST-')) {
        alert("Reset demo is only available in isolated Guest Mode.");
        return;
      }
      if (!confirm("Reset guest environment to clean initial state?")) return;
      try {
        const resp = await fetch('/api/auth/reset-demo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: currentUserSession.user_id })
        });
        const data = await resp.json();
        if (data.status === 'success') {
          loadCustomerHomeData();
          loadCustomerOrdersData();
          loadCustomerRequestsData();
          alert("Guest demo data successfully reset to clean state.");
        }
      } catch (err) {
        console.error("Reset error", err);
      }
    }

    function switchToCustomerMode() {
      currentAppMode = 'customer';
      showAppChassis();

      // Show customer sidebar & header
      document.getElementById('sidebar-nav-customer').classList.remove('hidden');
      document.getElementById('sidebar-nav-evaluator').classList.add('hidden');
      document.getElementById('header-left-customer').classList.remove('hidden');
      document.getElementById('header-left-evaluator').classList.add('hidden');
      document.getElementById('floating-chat-btn-container').classList.remove('hidden');

      // Update Sidebar tags
      document.getElementById('sidebar-mode-label').innerText = "Customer Portal";
      document.getElementById('sidebar-mode-dot').className = "w-2 h-2 rounded-full bg-secondary-fixed";
      document.getElementById('sidebar-version-badge').innerText = "CUSTOMER v4.8";
      document.getElementById('sidebar-switch-mode-text').innerText = "Switch to Evaluator Console";
      document.getElementById('header-switch-view-label').innerText = "Evaluator Mission Control";

      // Sync user profile labels
      const u = currentUserSession || { username: 'Rahul Sharma', user_id: 'USER-CUST-DEMO', role: 'DEMO_CUSTOMER' };
      const initial = (u.username || 'RS').substring(0, 2).toUpperCase();
      document.getElementById('user-avatar-initials').innerText = initial;
      document.getElementById('user-display-name').innerText = u.username;
      document.getElementById('user-role-label').innerText = u.role === 'GUEST' ? "Guest Customer (Isolated)" : "Customer Account";
      
      const welcomeEl = document.getElementById('welcome-cust-name');
      if (welcomeEl) welcomeEl.innerText = (u.username || 'Customer').split(' ')[0];

      // Account Screen Sync
      const accName = document.getElementById('acc-name');
      if (accName) accName.innerText = u.username;
      const accAvatar = document.getElementById('acc-avatar');
      if (accAvatar) accAvatar.innerText = initial;
      const accCustId = document.getElementById('acc-cust-id');
      if (accCustId) accCustId.innerText = u.user_id.startsWith('GUEST-') ? u.user_id : 'CUST-101';
      const accUserId = document.getElementById('acc-user-id');
      if (accUserId) accUserId.innerText = u.user_id;
      const accEmail = document.getElementById('acc-email');
      if (accEmail) accEmail.innerText = u.email || 'customer@example.in';
      const accSessType = document.getElementById('acc-session-type');
      if (accSessType) accSessType.innerText = u.user_id.startsWith('GUEST-') ? 'Isolated Guest Demo' : 'Authenticated Customer';

      // Guest reset badge toggle
      const guestBadge = document.getElementById('guest-reset-badge');
      if (guestBadge) {
        if (u.user_id && u.user_id.startsWith('GUEST-')) {
          guestBadge.classList.remove('hidden');
        } else {
          guestBadge.classList.add('hidden');
        }
      }

      // Switch to customer home screen and load isolated customer state
      customerOrdersCache = [];
      switchScreen('customer-home');
      loadCustomerHomeData();
      loadCustomerOrdersData();
      loadCustomerRequestsData();
      loadDrawerChatHistory();
    }

    function switchToEvaluatorMode() {
      currentAppMode = 'evaluator';
      showAppChassis();

      // Show evaluator sidebar & header
      document.getElementById('sidebar-nav-customer').classList.add('hidden');
      document.getElementById('sidebar-nav-evaluator').classList.remove('hidden');
      document.getElementById('header-left-customer').classList.add('hidden');
      document.getElementById('header-left-evaluator').classList.remove('hidden');

      // Update Sidebar tags
      document.getElementById('sidebar-mode-label').innerText = "Evaluator Control";
      document.getElementById('sidebar-mode-dot').className = "w-2 h-2 rounded-full bg-secondary-fixed animate-pulse";
      document.getElementById('sidebar-version-badge').innerText = "AI-OPS v4.8";
      document.getElementById('sidebar-switch-mode-text').innerText = "Switch to Customer View";
      document.getElementById('header-switch-view-label').innerText = "Switch to Customer View";

      // Profile tags for evaluator
      document.getElementById('user-avatar-initials').innerText = "ER";
      document.getElementById('user-display-name').innerText = "Elena Rostova";
      document.getElementById('user-role-label').innerText = "Staff AI Architect (Evaluator)";

      // Switch to mission control screen
      switchScreen('mission-control');
      checkLLMStatus();
    }

    function toggleModeSwitch() {
      if (currentAppMode === 'customer') {
        switchToEvaluatorMode();
      } else {
        switchToCustomerMode();
      }
    }

    function openEvaluatorPortal() {
      if (currentUserSession && (currentUserSession.role === 'EVALUATOR' || currentUserSession.role === 'STAFF_ARCHITECT')) {
        switchToEvaluatorMode();
      } else {
        setAuthTab('evaluator');
        scrollToAuth('evaluator');
      }
    }

    // --- Data Loaders for Customer Experience ---

    async function loadCustomerHomeData() {
      const uid = (currentUserSession && currentUserSession.user_id) ? currentUserSession.user_id : 'USER-CUST-DEMO';
      try {
        const resp = await fetch(`/api/customer/home?user_id=${encodeURIComponent(uid)}`);
        const data = await resp.json();
        if (data.status === 'success' && data.activity) {
          const cust = data.activity.customer || {};
          const custName = cust.name || (currentUserSession ? currentUserSession.username : 'Customer');
          const initial = (custName || 'C').substring(0, 2).toUpperCase();

          // Dynamic Header & Profile Synchronization
          const welcomeEl = document.getElementById('welcome-cust-name');
          if (welcomeEl) welcomeEl.innerText = custName.split(' ')[0];

          const sideName = document.getElementById('sidebar-user-name');
          if (sideName) sideName.innerText = custName;
          const sideAvatar = document.getElementById('sidebar-avatar');
          if (sideAvatar) sideAvatar.innerText = initial;
          const userDisp = document.getElementById('user-display-name');
          if (userDisp) userDisp.innerText = custName;
          const userInit = document.getElementById('user-avatar-initials');
          if (userInit) userInit.innerText = initial;

          const roleLabel = document.getElementById('user-role-label');
          if (roleLabel) {
            roleLabel.innerText = uid.startsWith('GUEST-') ? 'Guest Customer (Isolated)' : (uid === 'USER-JAYDEV' ? 'Verified Customer' : 'Customer Account');
          }

          // Account Screen Elements
          const accName = document.getElementById('acc-name');
          if (accName) accName.innerText = custName;
          const accAvatar = document.getElementById('acc-avatar');
          if (accAvatar) accAvatar.innerText = initial;
          const accCustId = document.getElementById('acc-cust-id');
          if (accCustId) accCustId.innerText = cust.customer_id || (uid.startsWith('GUEST-') ? 'CUST-GUEST' : (uid === 'USER-JAYDEV' ? 'CUST-JAYDEV' : 'CUST-101'));
          const accUserId = document.getElementById('acc-user-id');
          if (accUserId) accUserId.innerText = uid;
          const accEmail = document.getElementById('acc-email');
          if (accEmail) accEmail.innerText = cust.email || (currentUserSession ? currentUserSession.email : 'customer@example.in');
          const accTrust = document.getElementById('acc-trust');
          if (accTrust) accTrust.innerText = `${cust.trust_score || 95}/100`;

          renderCustomerOrders(data.activity.recent_orders || [], 'cust-orders-list', 4);
          renderCustomerTimeline(data.activity.recent_cases || [], 'cust-timeline-list');
          
          const statOrders = document.getElementById('cust-stat-orders');
          if (statOrders) statOrders.innerText = (data.activity.recent_orders || []).length;
          const statCases = document.getElementById('cust-stat-cases');
          if (statCases) statCases.innerText = (data.activity.recent_cases || []).length;
          const statRefunds = document.getElementById('cust-stat-refunds');
          if (statRefunds) statRefunds.innerText = (data.activity.recent_refunds || []).length;
        }
      } catch (e) {
        console.error("Home data error", e);
      }
    }

    async function loadDrawerChatHistory() {
      const uid = (currentUserSession && currentUserSession.user_id) ? currentUserSession.user_id : 'USER-CUST-DEMO';
      const sessId = (currentUserSession && currentUserSession.session_id) ? currentUserSession.session_id : ('SESS-' + uid);
      const container = document.getElementById('drawer-messages');
      if (!container) return;

      try {
        const resp = await fetch(`/api/chat/history?user_id=${encodeURIComponent(uid)}&session_id=${encodeURIComponent(sessId)}`);
        const data = await resp.json();
        if (data.status === 'success') {
          const history = data.history || [];
          if (history.length === 0) {
            const custName = (currentUserSession && currentUserSession.username) ? currentUserSession.username.split(' ')[0] : 'there';
            container.innerHTML = `
              <div class="flex items-start gap-3 max-w-lg">
                <div class="w-8 h-8 rounded-xl bg-primary text-secondary-fixed flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 shadow-sm">
                  ⚡
                </div>
                <div class="bg-white p-4 rounded-2xl rounded-tl-sm border border-slate-200 shadow-sm text-xs text-slate-800 leading-relaxed">
                  Hello ${escapeHtml(custName)}! I am your ResolveX Autonomous Assistant. How can I help you with your orders, bookings, or payments today?
                </div>
              </div>
            `;
            return;
          }

          container.innerHTML = '';
          history.forEach(msg => {
            if (msg.role === 'user') {
              const uBubble = document.createElement('div');
              uBubble.className = "flex justify-end";
              uBubble.innerHTML = `<div class="chat-bubble-user p-4 max-w-md text-xs shadow-sm leading-relaxed">${escapeHtml(msg.content)}</div>`;
              container.appendChild(uBubble);
            } else {
              const botContainer = document.createElement('div');
              botContainer.className = "flex items-start gap-3 max-w-lg";
              botContainer.innerHTML = `
                <div class="w-8 h-8 rounded-xl bg-primary text-secondary-fixed flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 shadow-sm">
                  ⚡
                </div>
                <div class="chat-bubble-bot p-4 shadow-sm text-xs flex flex-col gap-2.5 leading-relaxed">
                  <div class="text-slate-900 leading-relaxed font-normal">${escapeHtml(msg.content)}</div>
                </div>
              `;
              container.appendChild(botContainer);
            }
          });
          container.scrollTop = container.scrollHeight;
        }
      } catch (e) {
        console.error('Error loading chat history:', e);
      }
    }

    async function loadCustomerOrdersData() {
      const uid = (currentUserSession && currentUserSession.user_id) ? currentUserSession.user_id : 'USER-CUST-DEMO';
      try {
        const resp = await fetch(`/api/customer/orders?user_id=${encodeURIComponent(uid)}`);
        const data = await resp.json();
        if (data.status === 'success') {
          customerOrdersCache = data.orders || [];
          renderCustomerOrders(customerOrdersCache, 'full-orders-list', 50);
        }
      } catch (e) {
        console.error("Orders data error", e);
      }
    }

    async function loadCustomerRequestsData() {
      const uid = (currentUserSession && currentUserSession.user_id) ? currentUserSession.user_id : 'USER-CUST-DEMO';
      try {
        const resp = await fetch(`/api/customer/requests?user_id=${encodeURIComponent(uid)}`);
        const data = await resp.json();
        if (data.status === 'success') {
          renderCustomerRequestsList(data.cases || [], data.refunds || []);
        }
      } catch (e) {
        console.error("Requests data error", e);
      }
    }

    function renderCustomerOrders(orders, containerId, limit = 50) {
      const container = document.getElementById(containerId);
      if (!container) return;
      if (!orders || orders.length === 0) {
        container.innerHTML = '<div class="text-xs text-slate-500 py-6 text-center">No orders found.</div>';
        return;
      }

      const slice = orders.slice(0, limit);
      container.innerHTML = slice.map(o => {
        const prov = o.provider || 'Generic Merchant';
        let badgeColor = "bg-slate-100 text-slate-700";
        if (prov === 'RedBus') badgeColor = "bg-red-50 text-red-700 border border-red-200";
        else if (prov === 'MakeMyTrip') badgeColor = "bg-blue-50 text-blue-700 border border-blue-200";
        else if (prov === 'Amazon') badgeColor = "bg-amber-50 text-amber-800 border border-amber-200";
        else if (prov === 'Flipkart') badgeColor = "bg-yellow-50 text-yellow-800 border border-yellow-200";
        else if (prov === 'Swiggy') badgeColor = "bg-orange-50 text-orange-700 border border-orange-200";

        let statusBadge = "bg-slate-100 text-slate-700";
        if (o.order_status === 'DELIVERED') statusBadge = "bg-emerald-50 text-emerald-700 font-bold";
        else if (o.order_status === 'FAILED') statusBadge = "bg-red-50 text-red-700 font-bold";
        else if (o.order_status === 'CANCELLED') statusBadge = "bg-slate-200 text-slate-800 font-bold";

        return `
          <div class="p-4 rounded-2xl bg-white border border-slate-200 hover:border-slate-300 transition-all shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center font-bold text-slate-700 shrink-0 mt-0.5">
                <span class="material-symbols-outlined text-[20px]">receipt</span>
              </div>
              <div class="flex flex-col gap-0.5">
                <div class="flex items-center gap-2">
                  <span class="font-grotesk font-bold text-xs text-slate-900">${escapeHtml(o.order_id)}</span>
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${badgeColor}">${escapeHtml(prov)}</span>
                  <span class="text-[10px] px-2 py-0.5 rounded-full ${statusBadge}">${escapeHtml(o.order_status)}</span>
                </div>
                <span class="text-xs text-slate-700 font-medium">${escapeHtml(o.item_details || 'Item Checkout')}</span>
                <span class="text-[11px] text-slate-400 font-mono">Amount: ₹${Number(o.amount).toLocaleString('en-IN')} • ${escapeHtml(o.creation_timestamp || '')}</span>
              </div>
            </div>

            <div class="flex items-center gap-2 shrink-0">
              <button onclick="reportIssueForOrder('${escapeHtml(o.order_id)}', '${escapeHtml(prov)}', ${o.amount}, '${escapeHtml(o.item_details || '')}')" class="px-3.5 py-1.5 rounded-full bg-primary hover:bg-primary/90 text-secondary-fixed text-xs font-grotesk font-bold transition-all shadow-xs flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[14px]">report_problem</span>
                <span>Report Issue</span>
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    function renderCustomerTimeline(cases, containerId) {
      const container = document.getElementById(containerId);
      if (!container) return;
      if (!cases || cases.length === 0) {
        container.innerHTML = '<div class="text-xs text-slate-500 py-6 text-center">No active cases.</div>';
        return;
      }

      container.innerHTML = cases.map(c => `
        <div class="p-3.5 rounded-2xl bg-white border border-slate-200 flex items-start gap-3 text-xs">
          <div class="w-8 h-8 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700 shrink-0 mt-0.5">
            <span class="material-symbols-outlined text-[16px]">receipt_long</span>
          </div>
          <div class="flex flex-col gap-1 w-full">
            <div class="flex items-center justify-between">
              <span class="font-grotesk font-bold text-slate-900">${escapeHtml(c.case_id)}</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">${escapeHtml(c.status)}</span>
            </div>
            <p class="text-slate-700 font-medium">${escapeHtml(c.issue)}</p>
            ${c.resolution ? `<p class="text-slate-500 text-[11px] bg-slate-50 p-2 rounded-lg border border-slate-100">✓ ${escapeHtml(c.resolution)}</p>` : ''}
          </div>
        </div>
      `).join('');
    }

    function renderCustomerRequestsList(cases, refunds) {
      const container = document.getElementById('full-requests-list');
      if (!container) return;

      const totalCount = cases.length + refunds.length;
      document.getElementById('req-stat-total').innerText = totalCount;
      const resolvedCount = cases.filter(c => c.status === 'RESOLVED' || c.status === 'RESOLVED_AUTO').length + refunds.length;
      document.getElementById('req-stat-resolved').innerText = resolvedCount;
      document.getElementById('req-stat-bank').innerText = refunds.length;

      let html = '';

      // Refunds cards first
      refunds.forEach(rf => {
        html += `
          <div class="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="font-grotesk font-bold text-xs text-slate-900">${escapeHtml(rf.refund_id)}</span>
                <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-secondary-fixed text-on-secondary-fixed">REFUND INITIATED</span>
                <span class="text-xs font-mono font-bold text-emerald-600">₹${Number(rf.amount).toLocaleString('en-IN')}</span>
              </div>
              <span class="text-[11px] text-slate-400">${escapeHtml(rf.initiated_timestamp || '')}</span>
            </div>
            <p class="text-xs text-slate-700">Autonomous payment reversal initiated via payment gateway API.</p>
            <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-[11px] font-mono flex flex-wrap items-center justify-between text-slate-700">
              <span>Bank ARN: <b>${escapeHtml(rf.bank_reference)}</b></span>
              <span>Expected Credit: <b>${escapeHtml(rf.expected_completion)}</b></span>
              <span>Initiated By: <b>${escapeHtml(rf.initiated_by)}</b></span>
            </div>
          </div>
        `;
      });

      // Cases
      cases.forEach(c => {
        let stClass = "bg-slate-100 text-slate-700";
        if (c.status.includes('RESOLVED')) stClass = "bg-emerald-50 text-emerald-700 font-bold";
        else if (c.status.includes('ESCALATED')) stClass = "bg-amber-50 text-amber-700 font-bold";

        html += `
          <div class="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="font-grotesk font-bold text-xs text-slate-900">${escapeHtml(c.case_id)}</span>
                <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${stClass}">${escapeHtml(c.status)}</span>
                <span class="text-[10px] font-semibold text-slate-500">${escapeHtml(c.category)}</span>
              </div>
              <span class="text-[11px] text-slate-400">${escapeHtml(c.created_time || '')}</span>
            </div>
            <p class="text-xs text-slate-800 font-medium">${escapeHtml(c.issue)}</p>
            ${c.resolution ? `<div class="p-2 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-600"><b>Resolution:</b> ${escapeHtml(c.resolution)}</div>` : ''}
          </div>
        `;
      });

      if (!html) {
        container.innerHTML = '<div class="text-xs text-slate-500 py-8 text-center">No recent requests or active refund cases.</div>';
      } else {
        container.innerHTML = html;
      }
    }

    function setOrderCategoryFilter(cat) {
      document.querySelectorAll('.order-filter-btn').forEach(b => {
        if (b.getAttribute('data-cat') === cat) {
          b.className = "order-filter-btn px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-900 text-secondary-fixed shadow-sm";
        } else {
          b.className = "order-filter-btn px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200";
        }
      });

      if (cat === 'ALL') {
        renderCustomerOrders(customerOrdersCache, 'full-orders-list', 50);
      } else {
        const filtered = customerOrdersCache.filter(o => (o.provider || '').toLowerCase().includes(cat.toLowerCase()));
        renderCustomerOrders(filtered, 'full-orders-list', 50);
      }
    }

    function filterCustomerOrders() {
      const query = (document.getElementById('order-filter-search').value || '').toLowerCase();
      const filtered = customerOrdersCache.filter(o => 
        (o.order_id || '').toLowerCase().includes(query) ||
        (o.provider || '').toLowerCase().includes(query) ||
        (o.item_details || '').toLowerCase().includes(query)
      );
      renderCustomerOrders(filtered, 'full-orders-list', 50);
    }

    function reportIssueForOrder(orderId, provider, amount, item) {
      toggleChatDrawer(true);
      const prompt = `I need help with my ${provider} order #${orderId} (${item}). Amount: ₹${amount}.`;
      document.getElementById('drawer-input').value = prompt;
      sendDrawerMessage();
    }

    function applyPromptChip(text) {
      const homeInput = document.getElementById('cust-home-input');
      if (homeInput) homeInput.value = text;
      toggleChatDrawer(true);
      const drawerInput = document.getElementById('drawer-input');
      if (drawerInput) drawerInput.value = text;
    }

    function applyDrawerChip(text) {
      const drawerInput = document.getElementById('drawer-input');
      if (drawerInput) {
        drawerInput.value = text;
        sendDrawerMessage();
      }
    }

    function submitCustomerIssueFromHome() {
      const homeInput = document.getElementById('cust-home-input');
      const val = (homeInput ? homeInput.value : '').trim();
      if (!val) return;
      toggleChatDrawer(true);
      const drawerInput = document.getElementById('drawer-input');
      if (drawerInput) {
        drawerInput.value = val;
        sendDrawerMessage();
      }
    }

    // --- Floating Chat Drawer Controller ---

    function toggleChatDrawer(open) {
      const drawer = document.getElementById('chat-drawer');
      if (open) {
        drawer.classList.remove('hidden');
        document.getElementById('drawer-input').focus();
      } else {
        drawer.classList.add('hidden');
      }
    }

    function handleDrawerKeyDown(e) {
      if (e.key === 'Enter') {
        sendDrawerMessage();
      }
    }

    function clearCurrentConversation() {
      const uid = (currentUserSession && currentUserSession.user_id) ? currentUserSession.user_id : 'USER-CUST-DEMO';
      const sessId = (currentUserSession && currentUserSession.session_id) ? currentUserSession.session_id : ('SESS-' + uid);
      fetch('/api/chat/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: uid, session_id: sessId })
      }).catch(() => {});

      const container = document.getElementById('drawer-messages');
      if (container) {
        container.innerHTML = `
          <div class="flex items-start gap-3 max-w-lg">
            <div class="w-8 h-8 rounded-xl bg-primary text-secondary-fixed flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 shadow-sm">
              ⚡
            </div>
            <div class="flex flex-col gap-1.5 bg-white p-4 rounded-2xl rounded-tl-sm border border-slate-200 shadow-sm text-xs text-slate-800 leading-relaxed">
              <span class="font-grotesk font-bold text-slate-900">ResolveX Assistant</span>
              <p>Conversation reset. How can I assist you with your orders or transactions today?</p>
            </div>
          </div>
        `;
      }
    }

    async function sendDrawerMessage() {
      const input = document.getElementById('drawer-input');
      const text = (input ? input.value : '').trim();
      if (!text) return;

      input.value = '';
      const container = document.getElementById('drawer-messages');

      // Append user bubble
      const userBubble = document.createElement('div');
      userBubble.className = "flex justify-end";
      userBubble.innerHTML = `
        <div class="chat-bubble-user p-4 max-w-md text-xs shadow-sm leading-relaxed">
          ${escapeHtml(text)}
        </div>
      `;
      container.appendChild(userBubble);
      container.scrollTop = container.scrollHeight;

      // Loading placeholder
      const loadingBubble = document.createElement('div');
      loadingBubble.className = "flex items-start gap-3 max-w-lg";
      loadingBubble.id = "drawer-loading-bubble";
      loadingBubble.innerHTML = `
        <div class="w-8 h-8 rounded-xl bg-primary text-secondary-fixed flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 shadow-sm">
          ⚡
        </div>
        <div class="bg-white p-4 rounded-2xl rounded-tl-sm border border-slate-200 shadow-sm text-xs text-slate-500 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-secondary-fixed animate-ping"></span>
          <span>ResolveX is investigating telemetry & policies...</span>
        </div>
      `;
      container.appendChild(loadingBubble);
      container.scrollTop = container.scrollHeight;

      const uid = (currentUserSession && currentUserSession.user_id) ? currentUserSession.user_id : 'USER-CUST-DEMO';
      const sessId = (currentUserSession && currentUserSession.session_id) ? currentUserSession.session_id : ('SESS-' + uid);

      try {
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: text,
            user_id: uid,
            session_id: sessId
          })
        });
        const data = await resp.json();
        
        const loader = document.getElementById('drawer-loading-bubble');
        if (loader) loader.remove();

        const botContainer = document.createElement('div');
        botContainer.className = "flex items-start gap-3 max-w-lg";

        const custResp = data.customer_response || {};
        const headline = custResp.headline || (data.status === 'success' ? "✓ Issue Resolved" : "Assistant Response");
        const badge = custResp.badge || "Verified Decision";
        const replyText = data.reply || custResp.explanation_text || "Your issue has been processed.";
        const whatWeDid = custResp.what_we_did || "";
        const reference = custResp.reference || "";
        const nextSteps = custResp.what_happens_next || "";
        const detailId = "detail-" + Math.random().toString(36).substring(2, 9);

        botContainer.innerHTML = `
          <div class="w-8 h-8 rounded-xl bg-primary text-secondary-fixed flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 shadow-sm">
            ⚡
          </div>
          <div class="flex flex-col gap-2 bg-white p-5 rounded-2xl rounded-tl-sm border border-slate-200 shadow-sm text-xs text-slate-800 leading-relaxed w-full">
            <div class="flex items-center justify-between border-b border-slate-100 pb-2">
              <span class="font-grotesk font-bold text-slate-900">${escapeHtml(headline)}</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-fixed">${escapeHtml(badge)}</span>
            </div>

            <p class="text-slate-800">${replyText.replace(/\\n/g, '<br/>')}</p>

            ${whatWeDid ? `<p class="text-emerald-700 font-semibold bg-emerald-50/70 p-2.5 rounded-xl border border-emerald-100">${escapeHtml(whatWeDid)}</p>` : ''}
            
            ${reference ? `<div class="font-mono text-[11px] text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-200"><b>${escapeHtml(reference)}</b></div>` : ''}
            
            ${nextSteps ? `<p class="text-[11px] text-slate-500"><b>Next:</b> ${escapeHtml(nextSteps)}</p>` : ''}

            <!-- Clarification Options if Ambiguity -->
            ${data.needs_clarification && data.clarification_options && data.clarification_options.length > 0 ? `
              <div class="flex flex-col gap-1.5 pt-2 border-t border-slate-100">
                <span class="text-[11px] font-semibold text-slate-500">Please choose one:</span>
                ${data.clarification_options.map(opt => `
                  <button onclick="applyDrawerChip('${escapeHtml(opt.text)}')" class="text-left px-3 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-800 transition-colors font-medium">
                    ${escapeHtml(opt.label)}
                  </button>
                `).join('')}
              </div>
            ` : ''}

            <!-- Expandable [ How did ResolveX decide? ] Accordion -->
            <div class="pt-2 border-t border-slate-100">
              <button onclick="document.getElementById('${detailId}').classList.toggle('hidden')" class="text-[11px] font-bold text-slate-700 hover:text-slate-900 flex items-center justify-between w-full py-1">
                <span class="flex items-center gap-1.5"><span class="material-symbols-outlined text-[15px] text-secondary">psychology</span> How did ResolveX decide?</span>
                <span class="material-symbols-outlined text-[16px]">expand_more</span>
              </button>
              <div id="${detailId}" class="hidden mt-2 p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-700 flex flex-col gap-2">
                <div><b>1. Evidence Verified:</b> ${custResp.what_we_found ? custResp.what_we_found.join(' • ') : 'Gateway transaction and order ledgers cross-referenced.'}</div>
                <div><b>2. Policy Citation:</b> <span class="font-mono text-secondary font-bold">${data.pipeline_data?.technical_payload?.policy_applied || 'POL-REF-01 (Autonomous Settlement)'}</span></div>
                <div><b>3. Safety Guard (Critic):</b> <span class="text-emerald-700 font-semibold">${data.pipeline_data?.critic_guard?.safety_gates || 'Passed: Zero duplicate payout • Idempotency token verified'}</span></div>
                <div><b>4. Action Executed:</b> ${escapeHtml(whatWeDid || 'Autonomous bank payout API invoked')}</div>
                <div><b>5. Verification:</b> <span class="font-mono text-[11px] text-slate-600">${escapeHtml(reference || 'Settlement audit hash signed')}</span></div>
              </div>
            </div>
          </div>
        `;

        container.appendChild(botContainer);
        container.scrollTop = container.scrollHeight;

        // Refresh customer datasets if mutation took place
        if (data.pipeline_data) {
          loadCustomerHomeData();
          loadCustomerRequestsData();
        }
      } catch (err) {
        const loader = document.getElementById('drawer-loading-bubble');
        if (loader) loader.remove();
        console.error("Chat error", err);
      }
    }

    // Override switchScreen to handle both layers and update nav-btn styling cleanly
    window.switchScreen = function(screenId) {
      document.querySelectorAll('.screen-view').forEach(view => {
        view.classList.add('hidden');
      });

      const target = document.getElementById(`screen-${screenId}`);
      if (target) target.classList.remove('hidden');

      // Update Nav Buttons
      document.querySelectorAll('.nav-btn').forEach(btn => {
        const navTarget = btn.getAttribute('data-nav');
        if (navTarget === screenId) {
          btn.className = "nav-btn w-full flex items-center justify-between px-4 py-2.5 rounded-full transition-all bg-secondary-fixed text-on-secondary-fixed font-grotesk font-bold shadow-sm";
        } else {
          btn.className = "nav-btn w-full flex items-center gap-2.5 px-4 py-2.5 rounded-full text-[#c4c6cd] hover:bg-[#283044] hover:text-white transition-all font-grotesk font-semibold text-sm";
        }
      });

      if (screenId === 'enterprise-data') {
        loadEnterpriseData('tx');
      } else if (screenId === 'customer-orders') {
        loadCustomerOrdersData();
      } else if (screenId === 'customer-requests') {
        loadCustomerRequestsData();
      } else if (screenId === 'customer-home') {
        loadCustomerHomeData();
      }
    };

    // Page Init
    window.addEventListener('DOMContentLoaded', () => {
      const stored = localStorage.getItem('resolvex_user');
      const isEvalRoute = window.location.pathname.includes('/evaluator') || 
                          window.location.pathname.includes('/admin') || 
                          window.location.pathname.includes('/mission-control') ||
                          window.location.hash.includes('evaluator');

      if (stored) {
        try {
          currentUserSession = JSON.parse(stored);
        } catch(e) {}
      }

      if (currentUserSession) {
        if (currentUserSession.role === 'EVALUATOR' || currentUserSession.role === 'STAFF_ARCHITECT') {
          switchToEvaluatorMode();
        } else {
          switchToCustomerMode();
        }
      } else {
        // First screen is always Landing/Login
        showLandingView();
        if (isEvalRoute) {
          setAuthTab('evaluator');
        } else {
          setAuthTab('customer');
        }
      }

      // Init technical dashboard components
      checkLLMStatus();
      previewScenario('pg-504');
    });
"""

complete_js = '<script>\n' + orig_js + '\n' + customer_js + '\n</script>'

# 9. ASSEMBLE COMPLETE DOCUMENT
complete_html = (
    "<!DOCTYPE html>\n"
    '<html lang="en">\n'
    + head_combined[head_combined.find('<head>'):] + '\n'
    '<body class="bg-surface antialiased text-on-surface">\n\n'
    + landing_html + '\n\n'
    '  <!-- ========================================================================= -->\n'
    '  <!-- MAIN WORKSPACE CHASSIS                                                    -->\n'
    '  <!-- ========================================================================= -->\n'
    '  <div id="app-chassis" class="hidden">\n'
    + sidebar_html + '\n\n'
    '    <!-- Main Content Canvas Wrapper -->\n'
    '    <div class="pl-72 flex flex-col min-h-screen">\n'
    + header_html + '\n\n'
    '      <!-- Main Canvas Container -->\n'
    '      <main class="p-8 max-w-[1720px] w-full mx-auto flex flex-col gap-6">\n'
    + customer_screens_html + '\n\n'
    + tech_screens_html + '\n'
    '      </main>\n'
    '    </div>\n\n'
    + modals_html + '\n\n'
    + drawer_html + '\n'
    '  </div>\n\n'
    + complete_js + '\n'
    '</body>\n'
    '</html>\n'
)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(complete_html)

print("SUCCESS: frontend/index.html generated!")
print("Total size:", len(complete_html), "bytes")
