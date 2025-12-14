# Pricing Tiers - Product Requirements Document

## Executive Summary

This document defines the pricing strategy for an AI-powered task management platform. The strategy implements a sustainable freemium model with three tiers designed to:
- Acquire users through a generous free tier ($0.25/user/month cost)
- Convert 2-5% to paid plans
- Maintain 75%+ profit margins on paid tiers
- Scale cost-effectively using intelligent model routing

**Target Economics:**
- Free tier: -$0.25/user/month (customer acquisition cost)
- Pro tier: +$8.50/user/month profit (78% margin)
- Business tier: +$43/user/month profit (86% margin)

---

## Pricing Tiers

### Tier 1: Free (Community)

**Price:** $0

**AI Capabilities:**
- 50 AI task generations per month
- AI model: Claude Haiku 4.5 (speed-optimized)
- Response time: Standard queue
- Context limit: Current board state only

**Features:**
- Unlimited boards and tasks (manual creation)
- Basic task management (create, edit, delete, organize)
- Up to 3 boards
- Single user only
- Community support (forums, documentation)

**Technical Implementation:**
- Hard limit: 50 AI actions per calendar month
- Model: `claude-haiku-4-5` exclusively
- Rate limiting: Max 10 AI actions per hour
- Reset: Monthly on signup anniversary date
- Prompt caching: Enabled (90% input cost reduction)

**Estimated Cost:** $0.25/user/month (assuming full 50 action usage)
**Actual Average Cost:** $0.10-0.15/user/month (based on 20-30 actions/month typical usage)

---

### Tier 2: Pro (Individual)

**Price:** $10/month (billed monthly) or $96/year (20% discount)

**AI Capabilities:**
- 500 AI task generations per month
- AI model: Claude Sonnet 4.5 (quality-optimized)
- Response time: Priority queue
- Context limit: Full workspace history (last 30 days)
- Smart suggestions based on task patterns

**Features:**
- Everything in Free, plus:
- Unlimited boards
- Advanced AI features:
  - Task breakdown (split complex tasks into subtasks)
  - Smart prioritization suggestions
  - Time estimation
  - Context-aware task generation
- Priority email support (24-hour response SLA)
- Export to CSV, JSON
- Basic integrations (Google Calendar, Slack notifications)

**Overage Handling:**
- Additional actions: $0.02 per action (metered billing)
- Soft limit notification at 450 actions (90%)
- Hard limit at 600 actions unless overage billing enabled
- Option to upgrade to Business tier when approaching limits

**Technical Implementation:**
- Base: 500 AI actions per calendar month
- Model routing:
  - Simple tasks (<10 items, <200 chars): Haiku ($0.005/action)
  - Complex tasks: Sonnet 4.5 ($0.015/action)
- Weighted average cost: ~$0.007/action
- Rate limiting: Max 50 AI actions per hour
- Prompt caching: Enabled with extended context window
- Batch processing: Low-priority actions use Batch API (50% discount)

**Estimated Cost:** $1.50-3.50/user/month (based on 300 average actions)
**Target Profit:** $7-8.50/user/month (70-85% margin)

---

### Tier 3: Business (Teams)

**Price:** $25/month per user (minimum 3 users, billed monthly)
**Annual:** $250/year per user (17% discount)

**AI Capabilities:**
- 2,000 AI task generations per user per month
- AI model: Claude Sonnet 4.5 + Opus 4.5 for complex planning
- Response time: Highest priority queue
- Context limit: Full workspace + cross-team insights
- Advanced AI features:
  - Multi-project planning
  - Resource allocation suggestions
  - Risk identification
  - Dependency mapping

**Features:**
- Everything in Pro, plus:
- Team collaboration:
  - Unlimited team members (minimum 3)
  - Shared boards and workspaces
  - @mentions and comments
  - Team activity feeds
- Admin controls:
  - User management
  - Permission levels
  - Usage analytics dashboard
  - Audit logs
- Advanced integrations:
  - Jira, Asana, Linear sync
  - GitHub issues integration
  - API access (100 requests/day per user)
- Dedicated support:
  - 4-hour email response SLA
  - Monthly success check-in call
  - Onboarding assistance

**Overage Handling:**
- Pool actions across team (e.g., 3 users = 6,000 actions/month shared)
- Additional actions: $0.015 per action (lower than Pro)
- Annual plans: +20% overage buffer included

**Technical Implementation:**
- Base: 2,000 AI actions per user per calendar month
- Team pool: Sum of all user allowances, shared
- Intelligent model routing:
  - Quick actions: Haiku 4.5
  - Standard planning: Sonnet 4.5
  - Strategic planning (>50 tasks): Opus 4.5
- Weighted average cost: ~$0.008/action
- Rate limiting: Max 100 AI actions per hour per team
- Prompt caching: Enabled with team context
- Batch processing: Overnight batch jobs for bulk operations
- API rate limits: 100 requests/day/user (pooled)

**Estimated Cost:** $7/user/month (based on 800 average actions + infrastructure)
**Target Profit:** $18/user/month (72% margin)

---

## Feature Comparison Matrix

| Feature | Free | Pro | Business |
|---------|------|-----|----------|
| **AI Actions/month** | 50 | 500 (+overage) | 2,000/user (pooled) |
| **AI Model** | Haiku 4.5 | Sonnet 4.5 | Sonnet + Opus |
| **Boards** | 3 | Unlimited | Unlimited |
| **Team Size** | 1 | 1 | 3+ users |
| **Context Window** | Current board | 30 days | Full history |
| **Integrations** | None | Basic (2) | Advanced (10+) |
| **API Access** | ❌ | ❌ | ✅ 100 req/day |
| **Support** | Community | Email (24h) | Email (4h) + Calls |
| **Analytics** | Basic | Standard | Advanced |
| **Batch Operations** | ❌ | ✅ | ✅ Priority |
| **Export** | ❌ | CSV, JSON | All formats + API |
| **Price** | $0 | $10/mo | $25/mo/user |

---

## Technical Requirements

### 1. Usage Tracking System

**Requirements:**
- Track AI action count per user per billing cycle
- Differentiate action types (task generation, breakdown, suggestions)
- Real-time counter visible in UI
- Reset on billing anniversary date
- Store historical usage for analytics

**Implementation:**
```python
class UsageTracker:
    def track_ai_action(
        user_id: str,
        action_type: str,
        tokens_input: int,
        tokens_output: int,
        model: str,
        cost: float
    ) -> UsageRecord

    def get_current_usage(user_id: str) -> UsageStats
    def get_remaining_quota(user_id: str) -> int
    def check_quota_available(user_id: str) -> bool
```

**Storage:**
```sql
CREATE TABLE usage_records (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    billing_cycle_start DATE,
    action_type VARCHAR(50),
    tokens_input INT,
    tokens_output INT,
    model VARCHAR(50),
    cost_usd DECIMAL(10,6),
    created_at TIMESTAMP
);

CREATE INDEX idx_usage_user_cycle ON usage_records(user_id, billing_cycle_start);
```

### 2. Model Routing Logic

**Requirements:**
- Automatically select optimal model based on task complexity
- Free tier: Always use Haiku
- Pro tier: Route between Haiku (simple) and Sonnet (complex)
- Business tier: Route between Haiku/Sonnet/Opus

**Complexity Heuristics:**
```python
def select_model(user_tier: str, task_context: dict) -> str:
    if user_tier == "free":
        return "claude-haiku-4-5"

    # Analyze complexity
    task_count = task_context.get("expected_tasks", 5)
    description_length = len(task_context.get("description", ""))
    has_dependencies = task_context.get("dependencies", False)

    if user_tier == "pro":
        if task_count < 10 and description_length < 200:
            return "claude-haiku-4-5"  # Simple
        else:
            return "claude-sonnet-4-5"  # Complex

    if user_tier == "business":
        if task_count < 10 and description_length < 200:
            return "claude-haiku-4-5"
        elif task_count < 50 and not has_dependencies:
            return "claude-sonnet-4-5"
        else:
            return "claude-opus-4-5"  # Strategic planning
```

### 3. Prompt Caching Implementation

**Requirements:**
- Cache system prompts (90% cost reduction on input)
- Cache user workspace context for Pro/Business tiers
- Invalidate cache on significant context changes
- Track cache hit rate

**Implementation:**
```python
from anthropic import Anthropic

def generate_with_caching(
    system_prompt: str,
    user_context: str,
    user_message: str,
    tier: str
) -> Response:
    client = Anthropic()

    # System prompt is always cached
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        }
    ]

    # Cache context for Pro/Business
    if tier in ["pro", "business"]:
        messages[0]["content"].append({
            "type": "text",
            "text": user_context,
            "cache_control": {"type": "ephemeral"}
        })

    # User message (not cached)
    messages.append({
        "role": "user",
        "content": user_message
    })

    return client.messages.create(
        model=select_model(tier, parse_context(user_message)),
        messages=messages
    )
```

### 4. Rate Limiting

**Requirements:**
- Prevent abuse through hourly rate limits
- Soft limits with warnings
- Hard limits with clear error messages
- Different limits per tier

**Limits:**
- Free: 10 actions/hour, 50/month
- Pro: 50 actions/hour, 500/month (+overage)
- Business: 100 actions/hour/team, 2000/month/user (pooled)

**Implementation:**
```python
from datetime import datetime, timedelta
from typing import Optional

class RateLimiter:
    def check_rate_limit(self, user_id: str, tier: str) -> tuple[bool, Optional[str]]:
        # Check hourly limit
        hourly_limit = {"free": 10, "pro": 50, "business": 100}[tier]
        hourly_count = self.get_hourly_count(user_id)

        if hourly_count >= hourly_limit:
            reset_time = self.get_hourly_reset_time()
            return False, f"Hourly limit reached. Resets at {reset_time}"

        # Check monthly limit
        monthly_count = self.get_monthly_count(user_id)
        monthly_limit = {"free": 50, "pro": 500, "business": 2000}[tier]

        if monthly_count >= monthly_limit:
            if tier == "pro":
                # Check if overage enabled
                if not self.is_overage_enabled(user_id):
                    return False, "Monthly limit reached. Enable overage or upgrade?"
            else:
                reset_date = self.get_billing_cycle_reset(user_id)
                return False, f"Monthly limit reached. Resets on {reset_date}"

        # Soft limit warning (90%)
        if monthly_count >= monthly_limit * 0.9:
            warning = f"You've used {monthly_count}/{monthly_limit} actions this month"
            return True, warning

        return True, None
```

### 5. Overage Billing (Pro Tier)

**Requirements:**
- Optional overage billing (user must opt-in)
- Metered billing at $0.02/action
- Real-time cost estimation before action
- Monthly invoice with breakdown
- Configurable overage limit (safety cap)

**Implementation:**
```python
class OverageManager:
    def check_overage_consent(self, user_id: str) -> bool:
        """Check if user has enabled overage billing"""
        pass

    def calculate_overage_cost(self, action_count: int) -> float:
        """$0.02 per action over base quota"""
        return action_count * 0.02

    def record_overage_action(self, user_id: str) -> None:
        """Track overage action for billing"""
        pass

    def get_current_overage_cost(self, user_id: str) -> float:
        """Get current month's overage cost"""
        pass

    def check_overage_cap(self, user_id: str) -> bool:
        """Check if user has hit their safety cap ($50 default)"""
        current_cost = self.get_current_overage_cost(user_id)
        cap = self.get_user_overage_cap(user_id)
        return current_cost < cap
```

### 6. Team Pooling (Business Tier)

**Requirements:**
- Aggregate quota across team members
- Any team member can use pool until exhausted
- Track individual usage for analytics
- Admin visibility into team usage patterns

**Implementation:**
```python
class TeamQuotaManager:
    def get_team_quota(self, team_id: str) -> int:
        """Calculate total team quota (users * 2000)"""
        member_count = self.get_team_member_count(team_id)
        return member_count * 2000

    def get_team_usage(self, team_id: str) -> int:
        """Get total actions used by team this month"""
        pass

    def check_team_quota(self, team_id: str) -> bool:
        """Check if team has quota remaining"""
        usage = self.get_team_usage(team_id)
        quota = self.get_team_quota(team_id)
        return usage < quota

    def get_member_breakdown(self, team_id: str) -> dict[str, int]:
        """Get usage breakdown by team member"""
        pass
```

### 7. Batch Processing

**Requirements:**
- Queue non-urgent operations for batch processing
- Use Anthropic Batch API (50% cost discount)
- Process overnight or during low-usage periods
- Available for Pro and Business tiers

**Use Cases:**
- "Improve all task descriptions overnight"
- "Analyze all projects and suggest priorities"
- "Generate weekly summary reports"

**Implementation:**
```python
class BatchProcessor:
    def queue_batch_job(
        self,
        user_id: str,
        job_type: str,
        parameters: dict,
        priority: str = "low"
    ) -> str:
        """Queue a batch job, returns job_id"""
        pass

    def process_batch_jobs(self) -> None:
        """Process queued batch jobs (run via cron)"""
        jobs = self.get_pending_jobs()

        for job in jobs:
            # Use Batch API
            result = self.submit_to_batch_api(job)
            self.update_job_status(job.id, "processing")

    def get_job_status(self, job_id: str) -> dict:
        """Check batch job status"""
        pass
```

---

## Business Requirements

### 1. Stripe Integration

**Requirements:**
- Subscription management (Pro: $10/mo, Business: $25/mo/user)
- Metered billing for overage charges
- Annual plan discounts (Pro: $96/year, Business: $250/year/user)
- Automatic invoice generation
- Failed payment handling

**Stripe Products:**
```python
# Pro Tier
stripe.Product.create(
    name="Pro Plan - Monthly",
    description="500 AI actions/month, priority support",
    default_price_data={
        "currency": "usd",
        "unit_amount": 1000,  # $10.00
        "recurring": {"interval": "month"}
    }
)

# Pro Tier - Annual
stripe.Product.create(
    name="Pro Plan - Annual",
    description="500 AI actions/month, priority support",
    default_price_data={
        "currency": "usd",
        "unit_amount": 9600,  # $96.00 (20% discount)
        "recurring": {"interval": "year"}
    }
)

# Overage Metered Billing
stripe.Price.create(
    product="pro_plan",
    billing_scheme="tiered",
    tiers=[
        {
            "up_to": 500,
            "unit_amount": 0  # Included in base
        },
        {
            "up_to": "inf",
            "unit_amount": 2  # $0.02 per action
        }
    ]
)
```

### 2. User Onboarding Flows

**Free Tier Onboarding:**
1. Sign up (email + password or OAuth)
2. Welcome tour (3-step interactive guide)
3. First AI action: "Try generating tasks for: 'Plan my week'"
4. Show quota indicator (50 actions remaining)
5. Prompt to upgrade after 10 actions used

**Pro Tier Onboarding:**
1. Payment collection via Stripe
2. Extended welcome tour (advanced features)
3. Setup integrations (Google Calendar, Slack)
4. First strategic planning session
5. Email: "You have 500 actions this month"

**Business Tier Onboarding:**
1. Admin setup (invite team members)
2. Dedicated onboarding call (30 min)
3. Team workspace configuration
4. Integration setup assistance
5. Quarterly success check-in scheduled

### 3. Upgrade Prompts

**When to Show Upgrade Prompts:**

**Free → Pro:**
- After 25 actions used (50% quota): "You're getting great value! Unlock 10x more actions"
- When hitting 50 action limit: "Upgrade to Pro for 500 actions + advanced AI"
- When trying to use Pro features (integrations, exports)

**Pro → Business:**
- When user creates 3+ boards with different collaborators
- When approaching 500 action limit regularly (3 months in a row)
- When attempting team features

**Copy Examples:**
```
Free → Pro:
"You've used 45/50 free AI actions this month! 🎉
Upgrade to Pro for $10/month and get:
✓ 500 AI actions (10x more)
✓ Smarter AI (Claude Sonnet)
✓ Integrations with Google Calendar & Slack
✓ Priority support
[Upgrade Now] [Maybe Later]"

Pro → Business:
"It looks like you're collaborating with a team!
Business plan gives you:
✓ 2,000 actions per user (pooled across team)
✓ Unlimited collaboration
✓ Admin controls & analytics
✓ API access
$25/month per user (3 user minimum)
[Start Free Trial] [Learn More]"
```

### 4. Free Trial for Business Tier

**Requirements:**
- 14-day free trial (no credit card required)
- Full access to Business features
- Email reminders: Day 7, Day 12, Day 14
- Trial usage tracked separately (doesn't count against regular quota)
- Automatic conversion to paid if credit card on file

### 5. Usage Analytics Dashboard

**Free Tier:**
- Simple counter: "25/50 actions used this month"
- Bar chart of daily usage (last 7 days)

**Pro Tier:**
- Everything in Free, plus:
- Breakdown by action type (generation, breakdown, suggestions)
- Cost savings from batch processing
- Historical trends (last 6 months)

**Business Tier:**
- Everything in Pro, plus:
- Team usage breakdown (by member)
- Most active boards/projects
- Peak usage times
- ROI calculator (time saved vs. cost)
- Export usage reports (CSV)

**Implementation:**
```python
class AnalyticsDashboard:
    def get_usage_summary(self, user_id: str, tier: str) -> dict:
        return {
            "current_period": {
                "actions_used": 247,
                "quota": 500,
                "overage": 0,
                "cost": 0  # $0 for included actions
            },
            "breakdown": {
                "task_generation": 180,
                "task_breakdown": 45,
                "smart_suggestions": 22
            },
            "daily_trend": [12, 8, 15, 20, 18, 25, 30],  # Last 7 days
            "projected_end_of_month": 420  # Forecast
        }

    def get_team_analytics(self, team_id: str) -> dict:
        """Business tier only"""
        return {
            "team_quota": 6000,
            "team_usage": 3450,
            "member_breakdown": {
                "user_1": 1200,
                "user_2": 1500,
                "user_3": 750
            },
            "top_boards": [
                {"name": "Q1 Planning", "actions": 890},
                {"name": "Product Roadmap", "actions": 670}
            ]
        }
```

---

## Migration & Rollout Plan

### Phase 1: Backend Infrastructure (Week 1-2)
- [ ] Implement usage tracking system
- [ ] Build model routing logic
- [ ] Add prompt caching
- [ ] Create rate limiting middleware
- [ ] Set up Stripe products and pricing

### Phase 2: User-Facing Features (Week 3-4)
- [ ] Add usage quota indicators to UI
- [ ] Build pricing page
- [ ] Implement upgrade flows
- [ ] Create analytics dashboards (per tier)
- [ ] Design and implement upgrade prompts

### Phase 3: Business Tier Features (Week 5-6)
- [ ] Team management (invite, remove, roles)
- [ ] Team quota pooling
- [ ] Admin analytics dashboard
- [ ] API access and documentation
- [ ] Batch processing queue

### Phase 4: Billing & Overage (Week 7)
- [ ] Stripe subscription webhooks
- [ ] Overage billing implementation
- [ ] Invoice generation
- [ ] Failed payment handling
- [ ] Refund workflows

### Phase 5: Testing & Launch (Week 8)
- [ ] Beta test with 20 users per tier
- [ ] Load testing (simulate 1,000 concurrent users)
- [ ] Cost monitoring dashboard (internal)
- [ ] Support documentation
- [ ] Public launch

---

## Success Metrics

### Financial Metrics
- **Target Conversion Rate:** 2-5% (free → paid)
- **Target Monthly Recurring Revenue (MRR):** $5,000 by Month 6
- **Customer Acquisition Cost (CAC):** <$50 per paying customer
- **Lifetime Value (LTV):** >$200 per customer (20+ month retention)
- **LTV/CAC Ratio:** >4:1

### Usage Metrics
- **Free Tier:**
  - Average actions/user/month: 20-30 (target)
  - % users hitting limit: <20%
  - Activation rate: >50% (used at least 1 AI action)

- **Pro Tier:**
  - Average actions/user/month: 250-350
  - % users with overage: <10%
  - Churn rate: <5% per month

- **Business Tier:**
  - Average actions/user/month: 800-1,200
  - Team size: Average 5 users per team
  - Churn rate: <3% per month

### Cost Metrics
- **AI Cost per Tier:**
  - Free: $0.10-0.25/user/month (actual)
  - Pro: $1.50-3.50/user/month
  - Business: $6-8/user/month

- **Profit Margins:**
  - Pro: >75%
  - Business: >70%

### Product Metrics
- **AI Quality:**
  - Task generation satisfaction: >4.0/5.0
  - % tasks marked as "helpful": >70%
  - Model routing accuracy: >85% (right model for complexity)

- **Performance:**
  - AI response time (p95): <3 seconds
  - Cache hit rate: >60%
  - Batch job completion: <12 hours

---

## Risk Mitigation

### Risk 1: Free Tier Abuse
**Scenario:** Users create multiple accounts to get unlimited free actions

**Mitigation:**
- Email verification required
- IP-based rate limiting (max 3 accounts per IP)
- Phone verification for suspicious signups
- ML-based fraud detection (flag unusual patterns)
- Manual review queue for high-usage free accounts

### Risk 2: Unexpectedly High AI Costs
**Scenario:** Users generate much longer outputs than estimated, 10x cost increase

**Mitigation:**
- Output token limits per tier (Free: 1000, Pro: 2000, Business: 4000)
- Real-time cost monitoring alerts (Slack notification if daily spend >$100)
- Automatic model downgrade if costs spike (Sonnet → Haiku)
- Kill switch to disable AI for specific users
- Weekly cost review meetings

### Risk 3: Low Conversion Rate
**Scenario:** <1% conversion from free to paid

**Mitigation:**
- A/B test upgrade prompts (messaging, timing, design)
- Exit surveys for churned users
- Freemium limits adjustment (reduce to 25 actions if needed)
- Add "Pro trial" for 7 days (give users taste of better AI)
- Email nurture campaigns

### Risk 4: High Churn Rate
**Scenario:** >10% monthly churn on paid plans

**Mitigation:**
- Exit surveys (understand why users leave)
- Retention campaigns (offer discounts to churning users)
- Usage-based engagement (email if no activity for 7 days)
- Feature requests (build what users want)
- Downgrade option (Pro → Free instead of cancel)

---

## Competitive Analysis

### Notion AI
- **Pricing:** $20/month (no free tier)
- **Model:** Unlimited AI within subscription
- **Our Advantage:** Lower cost ($10), generous free tier

### ChatGPT Plus
- **Pricing:** $20/month
- **Free Tier:** ~15 messages per 3 hours
- **Our Advantage:** Task-specific, integrated workflow

### Todoist
- **Pricing:** $5/month (no AI features in 2025)
- **AI Features:** None native (potential future competitor)
- **Our Advantage:** AI-first approach

### Linear
- **Pricing:** $8/user/month (engineering teams)
- **AI Features:** Limited (autocomplete, templates)
- **Our Advantage:** More powerful AI, better for individuals

**Key Differentiator:** We're the only task management tool offering a generous AI free tier (50 actions) at the lowest paid tier price point ($10) with intelligent cost optimization.

---

## Open Questions & Decisions Needed

### 1. Overage Pricing for Business Tier
**Question:** Should Business tier overage be cheaper than Pro?
**Options:**
- A) $0.02/action (same as Pro)
- B) $0.015/action (25% discount for volume)
- C) No overage, upgrade to unlimited ($50/user)

**Recommendation:** Option B ($0.015) - rewards teams with lower per-action cost

### 2. Free Trial for Pro Tier
**Question:** Should we offer a free trial for Pro?
**Options:**
- A) No trial (reduces friction for $10/month)
- B) 7-day trial, credit card required
- C) 14-day trial, no credit card required

**Recommendation:** Option A - $10 is low enough to skip trial, reduces churn from forgotten subscriptions

### 3. Annual Plan Discount
**Question:** What discount for annual plans?
**Options:**
- A) 15% (Pro: $102/year, Business: $255/year)
- B) 20% (Pro: $96/year, Business: $250/year) ← Current
- C) 25% (Pro: $90/year, Business: $225/year)

**Recommendation:** Option B (20%) - standard SaaS discount, good balance

### 4. API Access for Pro Tier
**Question:** Should Pro tier get API access?
**Options:**
- A) No API (Business only)
- B) Limited API (25 requests/day)
- C) Full API access (same as Business)

**Recommendation:** Option A - keep API as Business differentiator

### 5. Model Selection for Free Tier
**Question:** Should free tier ever use Sonnet?
**Options:**
- A) Always Haiku (keeps costs predictable)
- B) First 10 actions use Sonnet (better first impression)
- C) Weekend actions use Sonnet (off-peak usage)

**Recommendation:** Option B - better activation, minimal cost impact ($0.10 extra)

---

## Implementation Checklist

### Backend
- [ ] Database schema for usage tracking
- [ ] Model routing logic with complexity detection
- [ ] Prompt caching implementation
- [ ] Rate limiting middleware (hourly + monthly)
- [ ] Stripe webhook handlers (subscription events)
- [ ] Overage billing calculation
- [ ] Team quota pooling logic
- [ ] Batch processing queue
- [ ] Cost monitoring alerts
- [ ] Analytics data aggregation

### Frontend
- [ ] Pricing page with tier comparison
- [ ] Usage quota indicator (navbar or dashboard)
- [ ] Upgrade prompts (contextual triggers)
- [ ] Stripe checkout integration
- [ ] Payment method management
- [ ] Usage analytics dashboard (per tier)
- [ ] Team management UI (Business)
- [ ] Overage consent flow (Pro)
- [ ] Invoice viewing

### Infrastructure
- [ ] Stripe account setup
- [ ] Anthropic API key management (separate for prod/dev)
- [ ] Environment variables (pricing config)
- [ ] Monitoring dashboards (Datadog/Grafana)
- [ ] Alerting rules (cost spikes, errors)
- [ ] Backup/restore procedures

### Documentation
- [ ] User guide: Understanding your quota
- [ ] User guide: How overage billing works
- [ ] User guide: Team management (Business)
- [ ] API documentation (Business tier)
- [ ] Support articles: Billing and payments
- [ ] Internal runbook: Handling refunds/disputes

### Testing
- [ ] Unit tests for usage tracking
- [ ] Unit tests for model routing
- [ ] Integration tests for Stripe webhooks
- [ ] Load tests (1,000 concurrent users)
- [ ] Cost simulation tests
- [ ] End-to-end upgrade flows
- [ ] Security audit (payment handling)

### Launch
- [ ] Beta testing (20 users per tier, 2 weeks)
- [ ] Pricing page A/B test setup
- [ ] Customer support training
- [ ] Launch announcement (email, blog, social)
- [ ] Monitor first 48 hours closely
- [ ] Weekly review for first month

---

## Appendix: Cost Calculations

### Detailed Cost Breakdown

**Free Tier (Haiku 4.5):**
```
Input:  1,150 tokens @ $1/M    = $0.00115
Output:   750 tokens @ $5/M    = $0.00375
With caching (90% input):      = $0.00011 + $0.00375 = $0.00386
Per action cost: $0.004

50 actions × $0.004 = $0.20/user/month
```

**Pro Tier (70% Haiku, 30% Sonnet):**
```
Haiku actions (350):  350 × $0.004 = $1.40
Sonnet actions (150): 150 × $0.015 = $2.25
Total: $3.65/user/month (for 500 actions)

Average: $0.0073/action
```

**Business Tier (50% Haiku, 40% Sonnet, 10% Opus):**
```
Actual usage: 800 actions/user/month
Haiku (400):  400 × $0.004 = $1.60
Sonnet (320): 320 × $0.015 = $4.80
Opus (80):    80 × $0.040  = $3.20
Total: $9.60/user/month

Average: $0.012/action
```

### Break-Even Analysis

**Free Tier:**
```
Cost per user: $0.20/month
To break even: Need 1 Pro user per 42 free users
At 2% conversion: Sustainable at any scale
```

**Pro Tier:**
```
Revenue: $10.00/month
Cost: $3.65 (AI) + $0.59 (Stripe) + $0.20 (infra) = $4.44
Profit: $5.56/user/month (56% margin)
```

**Business Tier:**
```
Revenue: $25.00/month
Cost: $9.60 (AI) + $0.73 (Stripe) + $0.50 (infra) = $10.83
Profit: $14.17/user/month (57% margin)
```

### ROI for Users

**Pro Tier Value Proposition:**
```
$10/month = $0.33/day

If each AI action saves 5 minutes of manual work:
500 actions × 5 min = 2,500 minutes = 41.6 hours saved/month

At $25/hour (avg knowledge worker):
Value created: 41.6 × $25 = $1,040/month
Cost: $10/month
ROI: 10,300%
```

This is the core sales message: "Spend $10, save 40+ hours."

---

## Contact & Approval

**Document Owner:** Product Management
**Last Updated:** 2025-12-14
**Status:** Draft - Awaiting Approval

**Approvers:**
- [ ] Product Lead
- [ ] Engineering Lead
- [ ] Finance Lead
- [ ] CEO

**Questions/Feedback:** [Link to discussion thread or email]
