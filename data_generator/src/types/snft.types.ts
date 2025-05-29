export enum TransactionType {
  BUY = "BUY",
  SELL = "SELL",
  TRANSFER = "TRANSFER",
  EXCHANGE = "EXCHANGE",
  OTHER = "OTHER",
  UNKNOWN = "UNKNOWN",
  MINT = "MINT",
}

// This seems more like a Property Type or general classification
export enum AssetType { // Renamed from NFTType for broader use if properties use it too
  SFR = "SFR", // Single Family Residence
  MULTIFAMILY = "MULTIFAMILY",
  OFFICE = "OFFICE",
  STORAGE = "STORAGE",
  INDUSTRIAL = "INDUSTRIAL",
  RETAIL = "RETAIL",
  HOTEL = "HOTEL",
  LAND = "LAND",
  AGRICULTURAL = "AGRICULTURAL",
  MIXED_USE = "MIXED_USE",
  ART = "ART", // Added for general NFTs
  COLLECTIBLE = "COLLECTIBLE", // Added for general NFTs
  MEMBERSHIP = "MEMBERSHIP", // Added for general NFTs
  EXPERIENCE = "EXPERIENCE", // Added for general NFTs
  OTHER_NFT = "OTHER_NFT", // For other SNFT categories
}

// --- Core Data Types ---
export type SNFT = {
  id: string;
  walletId: string;
  name: string; // This should map to 'title'
  description: string | null;
  imageUrl: string; // This should map to 'image'
  price: number; // This is numeric
  currency?: "ETH" | "USD" | string;
  createdAt: string;
  updatedAt?: string | null;
  transactions?: Transaction[];
  address: string;
  // Marketplace specific display/filter fields:
  creator?: string;
  dateListed?: string;
  status?: string;
  category?: AssetType | string;
  collectionId?: string;
  collectionName?: string;
  bidPrice?: string; // Display string
  numericBidPrice?: number;
  endTime?: string;
  badges?: string[];
  collectionInitials?: string;
};

export type Transaction = {
  // Using your provided definition
  id: string;
  walletId: string;
  type: TransactionType;
  // For 'nft' field, if Transaction can exist without an SNFT, it's nullable.
  // If a transaction is ALWAYS about one SNFT, then `nft: SNFT;`
  // However, an SNFT has transactions, creating a potential circular dependency if not careful with data fetching.
  // Often, a transaction might store nftId instead of the full object.
  // For this context, assuming it might be linked or not.
  nftId?: string; // ID of the SNFT involved, if any
  nft?: Partial<SNFT> | null; // Partial SNFT data or null if not SNFT-specific transaction
  amount: number; // Could be crypto amount or fiat amount depending on context
  currency?: string; // e.g., "ETH", "USD"
  createdAt: string; // ISO Date string
  updatedAt?: string | null; // ISO Date string
};
