export interface LedgerEntry {
  id: number;
  customer_id: number;
  business_id: number;
  entry_type: 'credit' | 'debit';
  amount: number;
  description?: string;
  image_url?: string;
  created_by_id: number;
  created_at: string;
}
export interface LedgerEntryCreate {
  customer_id: number;
  entry_type: 'credit' | 'debit';
  amount: number;
  description?: string;
  image_url?: string;
}
export interface LedgerEntryUpdate {
  customer_id:number;
  entry_type?: 'credit' | 'debit';
  amount?: number;
  description?: string;
  image_url?: string;
}
