# ✅ Bridges Market Gamification & DAO Platform – TODO.md

This file outlines current and planned development milestones for the gamified real estate platform powered by DAOs, SNFTs, badges, and community reputation.

---

## 🔧 CORE IMPLEMENTED

- [x] Initial Supabase schema: users, wallets, reputations, SNFTs, trades, auctions, orders, collections, user investments, etc.
- [x] Row-level security policies and triggers
- [x] XP tracking and badge earning
- [x] Reputation recalculation logic
- [x] Notifications for XP, mentions, badge achievements
- [x] DAO table with classification and voting metadata
- [x] Contractor DAO integration schema
- [x] Username mentions + link referencing
- [x] Real-time chat and message favoriting
- [x] Rate-limiting with Upstash Redis

---

## 🧠 IN PROGRESS

- [ ] BadgeNFT.sol (soulbound or claimable on-chain badges)
- [ ] Supabase Edge Function: Mint badge on earn event
- [ ] Avatar flare (badges visually decorate user/DAO profiles)
- [ ] Badge claim page (optional if not soulbound)
- [ ] Sharing/comments/replies with notification hooks
- [ ] Favorites system for messages, strategies, assets
- [ ] UserStats: last_active, activity rollups, XP counters
- [ ] Public strategy library with fork and rating features
- [ ] Daily recalculation of reputation scores (SQL cron)
- [ ] DAO-level ratings, reviews, ranks (non-voice, influence-only)
- [ ] SNFTs receive their own stars, likes, comments, favorites
- [ ] Mentions + gamified influence from public recognition

---

## 🔜 UPCOMING

- [ ] DAO-to-DAO bids & service agreements
- [ ] DAO Trust integration for real-world property/business tokenization
- [ ] Gamified real estate badge perks (e.g. vacation time, DAO invite)
- [ ] DAO leadership incentives based on growth contributions
- [ ] Voting logic for asset-backed vs service-only DAOs
- [ ] Trust abstraction layer (ERC + Supabase coordination)
- [ ] Badge-based role unlocking & token-based privilege access

---

## 🎖️ BADGES SYSTEM

- [ ] Badge Metadata (badges.json with IPFS support)
- [ ] Image prompt generation per badge
- [ ] 150+ tiered badge definitions (done)
- [ ] 5 God-tier badges with utility
- [ ] Badge-based marketplace perks or DAO governance multipliers

---

## ⚙️ DEV OPS

- [ ] Add support for multiple local Supabase projects (port variation)
- [ ] Secure production Postgres connections
- [ ] Improved SQL migration automation
- [ ] CI/CD for schema, badges, and XP engines

---

## 🏗 CONTRACTOR MODULE

- [ ] Contractor table linked to DAO
- [ ] Project history and star ratings
- [ ] Likes/comments embedded per contractor
- [ ] Future: Contractors can tokenize business ownership

---

## 🧭 DESIGN PRINCIPLES

- Gamify platform-wide participation: Not just trade/profit but chat, governance, advice
- Encourage healthy peer review through stars and badges
- Give early builders ongoing stake in platform’s growth
- Enable DAO composability and inter-dependency
