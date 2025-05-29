export interface PropertyListing {
  id: string;
  name: string;

  address: string;
  imageUrl: string;
  tokenSymbol: string;
  currentPrice: number;
  priceUnit: "USDC" | "ETH" | "USD";
  apy?: number;
  valuation: number;
  tokensOffered?: number; // For fractional ownership
  totalTokens?: number; // For fractional ownership
  isFavorite?: boolean;
  status: "For Sale" | "Auction" | "Rented" | "Sold";
  priceHistory?: { date: string; price: number }[]; // For charts
  ohlcHistory?: CandlestickDataPoint[];
  volumeHistory?: { time: UTCTimestamp; value: number; color?: string }[];
}

export interface OrderFormState {
  orderType: "buy" | "sell" | "bid"; // Should be handled by activeTab in OrderForm
  amount: string;
  pricePerToken?: string;
  slippage?: string; // Example advanced field
  duration?: string; // Example advanced field for bids
}

export interface CandlestickDataPoint {
  time: UTCTimestamp; // 'YYYY-MM-DD' or other UTCTimestamp compatible format
  open: number;
  high: number;
  low: number;
  close: number;
  value?: number; // For volume, if you map it to the same time points
  color?: string; // For volume bar color
}

import { UTCTimestamp } from "lightweight-charts";
// --- Import relevant interfaces from your global types ---

import { AssetType } from "./snft.types";

// --- Volume Data Point ---

export interface VolumeDataPoint {
  time: UTCTimestamp;
  value: number;
  color?: string;
}

// --- Property Asset (Represents the Tokenized Real Estate) ---
// Combining relevant fields from your SNFT and PropertyMarketplaceItem
export interface PropertyAsset {
  id: string; // From SNFT.id or PropertyMarketplaceItem.id
  name: string; // From SNFT.name or PropertyMarketplaceItem.title
  tokenSymbol: string; // New: e.g., "MBV" - Needs to be defined for each property
  description?: string | null; // From SNFT.description
  imageUrl: string; // From SNFT.imageUrl or PropertyMarketplaceItem.image
  address: string; // From SNFT.address or PropertyMarketplaceItem.location
  propertyType: AssetType; // From your AssetType enum (e.g., AssetType.SFR)
  status?: string; // From PropertyMarketplaceItem.status (e.g., "For Sale", "Rented")

  // Financials / Tokenomics
  valuation?: number; // From your previous PropertyListing or calculated
  totalTokens?: number; // From PropertyMarketplaceItem.totalTokens
  apy?: number; // From your previous PropertyListing or PropertyMarketplaceItem.roi (if parsed)

  // Linking to original SNFT ID if applicable
  underlyingSnftId?: string; // If this directly maps to an SNFT in your system

  // Fields from your PropertyMarketplaceItem
  dateListed?: string; // From PropertyMarketplaceItem.dateListed
  // Add other relevant fields from PropertyMarketplaceItem or SNFT as needed
  // e.g., creator, collectionName, etc.
}

// --- Trading Pair ---
export interface TradingPair {
  id: string; // e.g., "MBV_USDC"
  baseAssetId: string; // PropertyAsset.id
  baseAssetSymbol: string; // PropertyAsset.tokenSymbol
  quoteAssetSymbol: string; // e.g., "USDC", "ETH", "USDT" (standard crypto symbols)

  // Market Data for the Pair
  lastPrice: number;
  priceChange24hPercent?: number; // As a number, e.g., 5.3 for +5.3%
  high24h?: number;
  low24h?: number;
  volume24hBase?: number; // Volume in terms of the base asset (e.g., 100 MBV traded)
  volume24hQuote?: number; // Volume in terms of the quote asset (e.g., 150,000 USDC traded)

  // Chart History for the Pair
  ohlcHistory?: CandlestickDataPoint[];
  volumeHistory?: VolumeDataPoint[];

  isFavorite?: boolean;
  // Potentially link to an order book ID if you have one
  orderBookId?: string;
}

// --- User Investment (User's holding of a PropertyAsset token) ---
export interface UserInvestment {
  id: string; // Unique ID for this investment record
  userId: string; // From GlobalProfile.id or Profile.userId
  propertyAssetId: string; // PropertyAsset.id

  // For display convenience (can be looked up from PropertyAsset)
  propertyName: string;
  propertyTokenSymbol: string;
  propertyImageUrl: string;

  tokensOwned: number;
  avgBuyPricePerToken: number; // The average price they paid per token
  avgBuyPriceCurrency: string; // Currency of avgBuyPrice (e.g., "USDC", "ETH")

  // Calculated values (preferably on backend or derived on client)
  totalInvestmentValueOriginal: number; // In avgBuyPriceCurrency
  currentMarketValuePerToken?: number; // In a common quote currency (e.g., USDC from a primary pair)
  currentPortfolioValue?: number; // Total current value in a common quote currency (e.g., USDC)

  purchaseDate?: string; // Date of first/latest significant purchase
  status?: "Owned" | "Staked" | "ListedForSale" | "InBot"; // More detailed status
}

// --- AI Bot Configuration ---
export interface AIBotConfig {
  strategy: "Grid" | "DCA" | "ML_Trend" | "Arbitrage" | string; // Allow custom string
  tradingPairId: string; // Link to TradingPair.id
  investmentAmount: number; // Amount to allocate from user's balance
  quoteAssetForInvestment: string; // Which quote currency to use for investment (e.g., "USDC")

  riskLevel?: "Low" | "Medium" | "High";
  isActive?: boolean;
  createdAt?: string;

  // Strategy-specific parameters (optional)
  takeProfitPercent?: number;
  stopLossPercent?: number;
  gridLevels?: number;
  gridStepPercent?: number;
  dcaOrderSize?: number;
  dcaFrequency?: string; // e.g., "1h", "4h", "1d"
  // ... other params for ML_Trend, Arbitrage etc.
}

// --- Order Form State (For manual trading if kept) ---
export interface ManualOrderFormState {
  tradingPairId: string;
  orderType: "buy" | "sell";
  tradeType: "market" | "limit";
  amount: string; // Amount of base or quote asset
  isAmountInBase: boolean; // True if 'amount' is for base asset
  limitPrice?: string; // Only for limit orders
}

// --- Active Manual Order (If you track them client-side or fetch them) ---
export type ActiveManualOrder = {
  orderId: string;
  timestamp: number;
  // ... other fields like status, filledAmount etc.
} & ManualOrderFormState;

export type IntervalConfig = {
  quote: string;
  intervalSeconds: number;
  historyPoints: number;
  idSuffix?: string; // optional, e.g. "1H", "1D"
  trend?: "up" | "down" | "sideways";
  priceVolatility?: number;
  wickVolatility?: number;
  baseVolume?: number;
};

export const INTERVAL_LABELS: Record<string, string> = {
  "1s": "1 second",
  "1m": "1 minute",
  "5m": "5 minutes",
  "15m": "15 minutes",
  "1h": "1 hour",
  "6h": "6 hours",
  "1d": "1 day",
  "1w": "1 week",
  "1mo": "1 month",
};