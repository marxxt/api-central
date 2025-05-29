import { AssetType } from "./snft.types";

// types/index.ts
export * from "./ui.types";
export * from "./database.types";
export * from "./auction.types";
export * from "./snft.types";
export * from "./user.types";
export * from "./enum.types";
export * from "./trade.types";

// --- Marketplace Specific UI Types ---
// This Property type is for the "Properties" tab, distinct from an "SNFT Property"
export interface PropertyMarketplaceItem {
  id: number | string;
  title: string; // Corresponds to SNFT 'name'
  location: string; // Specific to physical properties
  price: string; // Display price, e.g., "$2,500,000"
  numericPrice: number; // For filtering/sorting
  tokenPrice?: string;
  totalTokens?: number;
  availableTokens?: number;
  image: string; // Corresponds to SNFT 'imageUrl'
  type?: AssetType | string; // e.g., "Residential", "Commercial", from AssetType enum
  roi?: string;
  dateListed: string; // ISO Date string (when listed on marketplace)
  createdAt: string; // ISO Date string (when property record was created)
  updatedAt?: string | null;
  status?: string; // e.g., "FOR SALE", "RENTED"
  collectionName?: string; // For display and potentially grouping
  collectionId?: string; // For filtering if properties are in collections
  // Add other property-specific fields
}

export interface CollectionItem {
  // For FilterSidebar
  id: string;
  name: string;
  color: string; // Tailwind CSS background color class
  count?: number; // Optional: number of items in this collection
}

export type SortOptionValue =
  | "date_listed_newest"
  | "date_listed_oldest"
  | "ending_soonest"
  | "ending_latest"
  | "price_lowest"
  | "price_highest";

export interface SortOption {
  value: SortOptionValue;
  label: string;
}


