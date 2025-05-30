# 📘 Standard Operating Procedure (SOP): Bridges Market Gamification System

**Project:** Bridges Market  
**Module:** Gamification & Engagement Layer  
**Last Updated:** 2025-05-29 18:48 UTC  
**Owner:** Platform Engineering  

---

## 🎯 Purpose

This SOP outlines the procedures, components, and operational requirements for maintaining and extending the gamification system powering XP, badges, notifications, and rate limits within the Bridges Market platform.

---

## 🧱 Core Components

| Component | Description |
|----------|-------------|
| **XP System** | Users earn XP via platform actions (comments, shares, kudos, etc.) |
| **Badges** | Soulbound NFTs (or claimable) awarded based on XP milestones, streaks, and community recognition |
| **User Stats** | Tracks engagement metrics: streaks, kudos, mentions, trades |
| **Rate Limiting** | Upstash Redis via Supabase Edge Functions prevents abuse |
| **Notifications** | In-app alerts for XP, badge unlocks, mentions, follows, and SNFT status |
| **Reputation** | Dynamic tier-based ranks calculated from multiple engagement factors |

---

## 🛠 Deployment Requirements

### ✅ Environment Variables
Must be configured in Supabase:
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`

### ✅ Supabase Edge Functions
Deploy from `/supabase/functions`:
```bash
supabase functions deploy rate_limit
```

### ✅ SQL Schema Files
Run in this order via Supabase SQL Editor or migration system:
1. `temp_corrected_schema.sql`
2. `gamification_core.sql`
3. `gamification_xp_badge_logic.sql`
4. `notifications_and_limits.sql`

---

## 🧬 Badge NFT Logic

Badges are earned via logic in SQL or backend functions, then:
- Stored in `user_badges` table
- Minted via Edge Function (future)
- Referenced from `user_profile_view` for GraphQL frontend

---

## 🚦 Rate Limiting Logic

Implemented in `rate_limit.ts`:
- Tracks actions per IP or user
- Returns JSON: `{{ allowed: true, remaining: 2, reset_in: 47 }}`
- Usage: Comment posting, mentions, login attempts

---

## 📩 Notifications

Sent upon:
- Earning XP or badges
- Being mentioned (`@username`)
- SNFT status changes (minted, expired)
- Being followed

Stored in `notifications` table and consumed via GraphQL query on frontend.

---

## 📌 Maintenance Tasks

| Task | Frequency | Owner |
|------|-----------|-------|
| Rotate Redis keys | Quarterly | DevOps |
| Recalculate reputation ranks | Daily cron | Supabase job |
| Monitor XP triggers | Weekly audit | Backend team |
| Cleanup expired SNFT drafts | Daily cron | Edge Function |

---

## 🧾 Future Features (from TODO.md)

- 🏗 BadgeNFT.sol for minting soulbound achievements
- 🧬 Minting Edge Function trigger on badge earn
- 🧑‍🎤 Avatar flare powered by badges
- 🎒 Badge claim UI with IPFS integration
- 🧠 DAO and SNFT ranking visibility

---

## 📎 References

- `badges_with_prompts.json` — AI generation prompts for badge art
- `rate_limit.ts` — Supabase Edge Function logic
- `gamification_todo.md` — living task list

---

## ✅ Contact

For questions, reach out to `engineering@bridgesmarket.com` or consult the internal Notion Gamification page.
