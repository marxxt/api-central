# TODO – Future Gamification Extensions for Bridges Market

This file outlines planned features beyond the CORE implementation.

---

## 🟡 COMPETITIVE Tier (Next Phase)

- [ ] Implement reputation-based permissions (e.g., voting, SNFT minting)
- [ ] Mentor system for high-reputation users (Advisor tags)
- [ ] Reputation decay for prolonged inactivity
- [ ] Weekly/seasonal quests (XP + badge rewards)
- [ ] Public-facing karma log per user (audit trail)

---

## 🔴 LEGENDARY Tier (Visionary Layer)

- [ ] Soulbound NFTs for achievements (non-transferable)
- [ ] DAO-based competition leagues and seasonal scoreboards
- [ ] Reward shop where XP can be exchanged for platform perks
- [ ] Cross-platform reputation export (EAS or Ceramic)
- [ ] AI model to detect and auto-reward helpful posts in real-time

## 🟣 Implementation To-Do (Extended Gamification & Identity)

| Feature            | Action                                                       |
|--------------------|--------------------------------------------------------------|
| 🏗 BadgeNFT.sol     | Mint badges on-chain (soulbound or claimable)               |
| 🧬 Minting logic    | Supabase Edge Function: call mint on badge earn             |
| 📩 Notification     | Add notifications table to alert on XP or badge earn        |
| 🧑‍🎤 Avatar flare    | Allow badges to decorate user profiles or DAO banners       |
| 🎒 Badge claim page | Build UI for “Claim this badge” (optional if soulbound)     |

## 🏛 Extended Real Estate & DAO Rewards – To-Do

| Feature                     | Action                                                                 |
|-----------------------------|------------------------------------------------------------------------|
| 🏖 Badge-linked Stays        | Create `property_rewards` table linking users, badges, and SNFT assets |
| 🎓 DAO Role Unlock via Badge | Design schema `badge_voting_roles` with tier-to-role mappings           |
| 📊 Badge-Based Voting Power | Extend DAO vote logic to include badge boosts in resolver/backend       |
| 📩 Stay Notification         | Auto-alert users when they earn a real estate reward badge              |
| 🧾 badge_unlocks.json        | Generate config mapping badges to real-world or DAO privileges          |
