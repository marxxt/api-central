import { UserRole } from "./enum.types";
import { SNFT, Transaction } from "./snft.types";

export type Wallet = {
  // Using your provided definition
  id: string;
  userId: string;
  address: string; // Wallet address string
  balance: number; // Primary balance, context needed for currency
  currency?: string; // e.g., "ETH", "USD"
  createdAt: string; // ISO Date string
  updatedAt?: string | null; // ISO Date string
  transactions?: Transaction[];
  nfts?: SNFT[]; // NFTs held by this wallet
};

export type Profile = {
  // Using your provided definition
  id: string;
  userId: string;
  email: string | null;
  firstName: string | null;
  lastName: string | null;
  role: UserRole;
  avatarUrl: string | null;
  bio: string | null;
  website: string | null;
  location: string | null;
  phone: string | null;
  createdAt: string; // ISO Date string
  updatedAt?: string | null; // ISO Date string
  wallets?: Wallet[];
};

export type Rank = "SSS" | "SS" | "S" | "A" | "B" | "C" | "D" | "F";

export type Reputation = {
  id: string;
  userId: string;
  score?: number;
  rank?: Rank;
  rankingPercentile?: string;
  lastUpdated?: string; // ISO Date string
  adjustedStakingYield?: string;
  forecastAccessLevel?: string;
};

export type User = Profile & {
  reputation?: Reputation;
};
