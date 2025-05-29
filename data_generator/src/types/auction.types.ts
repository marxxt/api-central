import { Profile, Reputation } from "./user.types";

export type AuctionType =
  | "Whole Project"
  | "Individual Tokens"
  | "RRNFT"
  | "Stay Reward";

export type AuctionStatus = "active" | "completed" | "pending" | "cancelled"; // Added more common statuses

export type participationStatus =
  | "low"
  | "medium"
  | "high"
  | "trending low"
  | "trending high";

export interface Seller {
  name: string;
  reputation: Omit<Reputation, "id" | "userId">; // Could be a more specific type like 'A+' | 'A' | 'B' etc.
  verified: boolean;
  // You might add more seller details later, e.g., avatarUrl, walletAddress
}

export interface BidHistoryEntry {
  id: string; // e.g., "bid-1"
  bidder: string; // Bidder's name or wallet address identifier
  amount: string; // e.g., "$2,300,000" - kept as string as in example, consider number for calculations
  time: string; // Relative time string, e.g., "2 hours ago"
  timestamp: number; // Unix timestamp (milliseconds since epoch)
}

export interface PropertyDetails {
  size: string; // e.g., "4,500 sq ft"
  bedrooms: number;
  bathrooms: number; // Could be number or string like "6.5"
  yearBuilt: number;
  amenities: string[];
  participationScore?: participationStatus; // e.g., "8.5%" - kept as string, optional as not all properties might have it upfront
  occupancyRate?: string; // e.g., "92%" - kept as string, optional
  // You could add more specific details:
  lotSize?: string;
  propertyTypeDetail?:
    | "Single Family"
    | "Condo"
    | "Townhouse"
    | "Multi-Family"
    | "Commercial"
    | "storage"
    | "industrial"
    | "retail"
    | "hotel"
    | "land";
  architecturalStyle?: string;
  additionalNotes?: string;
}

export interface Auction {
  id: number;
  type: AuctionType;
  title: string;
  location: string;
  description: string;
  totalTokens: number;
  tokenPrice?: string; // Price per token, e.g., "$250", optional if not applicable for all auction types
  reservePrice: string; // e.g., "$2,250,000" - kept as string
  buyNowPrice?: string; // Optional, e.g., "$2,500,000"
  currentBid: string; // e.g., "$2,300,000" - kept as string
  minBidIncrement: string; // e.g., "$10,000" - kept as string
  bidCount: number;
  endTime: string; // ISO string date format
  image: string; // Path to image or URL
  status: AuctionStatus;
  seller: Seller;
  bidHistory: BidHistoryEntry[];
  propertyDetails: PropertyDetails;
  createdAt?: Date;
  winner?: string; // Bidder ID of the winner after completion
  winningBid?: string;
  transactionHash?: string;
  daoContractAddress?: string;
  acceptedPaymentMethods?: PaymentMethod[];
  currentBidCrypto: string; // e.g., "4.7 ETH" - kept as string
  highestBidder?: Omit<HighestBidder, "id">; // Bidder ID of the highest bidder
  agreedToTerms?: boolean;
}

export interface PaymentMethod {
  id: string; // e.g., "eth", "usdc", "credit-card", "platform-bells"
  name: string; // e.g., "Ether", "USD Coin", "Credit Card", "$BELLS"
  symbol: string; // e.g., "ETH", "USDC", "CC", "$BELLS"
  iconSrc: string; // Path to the icon, e.g., "/icons/payments/ether.png"
  type: "crypto" | "fiat";
  contractAddress?: string; // Optional: for blockchain-based tokens
}

export interface Bid {
  id: string;
  amount: string;
  timestamp: string;
  bidder: Profile;
  auctionId: string;
}

export interface AuctionSettlement {
  auction: Auction;
  winner?: Profile;
  winningBid?: Bid;
  settled: boolean;
  reserveMet: boolean;
  message: string;
}

export interface SettlementNotification {
  title: string;
  message: string;
  type: string;
}

export interface SettlementNotifications {
  creatorNotification: SettlementNotification;
  winnerNotification?: SettlementNotification;
  otherBiddersNotification: SettlementNotification;
}

export interface HighestBidder extends Partial<Profile> {
  id: string;
  name: string;
  avatarUrl: string;
}
