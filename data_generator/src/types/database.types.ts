export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string
          user_id: string
          email: string | null
          first_name: string | null
          last_name: string | null
          role: string
          avatar_url: string | null
          bio: string | null
          website: string | null
          location: string | null
          phone: string | null
          created_at: string
          updated_at: string | null
        }
        Insert: {
          id?: string
          user_id: string
          email?: string | null
          first_name?: string | null
          last_name?: string | null
          role?: string
          avatar_url?: string | null
          bio?: string | null
          website?: string | null
          location?: string | null
          phone?: string | null
          created_at?: string
          updated_at?: string | null
        }
        Update: {
          id?: string
          user_id?: string
          email?: string | null
          first_name?: string | null
          last_name?: string | null
          role?: string
          avatar_url?: string | null
          bio?: string | null
          website?: string | null
          location?: string | null
          phone?: string | null
          created_at?: string
          updated_at?: string | null
        }
      }
      wallets: {
        Row: {
          id: string
          user_id: string
          address: string
          balance: number
          created_at: string
          updated_at: string | null
        }
        Insert: {
          id?: string
          user_id: string
          address: string
          balance?: number
          created_at?: string
          updated_at?: string | null
        }
        Update: {
          id?: string
          user_id?: string
          address?: string
          balance?: number
          created_at?: string
          updated_at?: string | null
        }
      }
      transactions: {
        Row: {
          id: string
          wallet_id: string
          type: string
          amount: number
          created_at: string
          updated_at: string | null
          nft_id: string | null
        }
        Insert: {
          id?: string
          wallet_id: string
          type: string
          amount: number
          created_at?: string
          updated_at?: string | null
          nft_id?: string | null
        }
        Update: {
          id?: string
          wallet_id?: string
          type?: string
          amount?: number
          created_at?: string
          updated_at?: string | null
          nft_id?: string | null
        }
      }
      nfts: {
        Row: {
          id: string
          wallet_id: string
          name: string
          description: string | null
          image_url: string
          price: number
          created_at: string
          updated_at: string | null
          address: string
        }
        Insert: {
          id?: string
          wallet_id: string
          name: string
          description?: string | null
          image_url: string
          price: number
          created_at?: string
          updated_at?: string | null
          address: string
        }
        Update: {
          id?: string
          wallet_id?: string
          name?: string
          description?: string | null
          image_url?: string
          price?: number
          created_at?: string
          updated_at?: string | null
          address?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      user_role: 'USER' | 'ADMIN'
      transaction_type: 'BUY' | 'SELL' | 'TRANSFER' | 'EXCHANGE' | 'OTHER' | 'UNKNOWN'
      nft_type: 'SFR' | 'MULTIFAMILY' | 'OFFICE' | 'STORAGE' | 'INDUSTRIAL' | 'RETAIL' | 'HOTEL' | 'LAND'
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}
