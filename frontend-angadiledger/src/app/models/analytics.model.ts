export interface LedgerEntry {
  id: number;
  customer_id: number;
  business_id: number;
  entry_type: 'credit' | 'debit';
  amount: number;
  description: string;
  image_url?: string;
  created_by_id: number;
  created_at: string;
}

export interface Customer {
  customer_id: number;
  customer_name: string;
  customer_email: string;
  total_payable: number;
  ledgers: LedgerEntry[];
}

export interface AnalyticsData {
  total_business_payable: number;
  total_business_receivable?: number;
  customers: Customer[];
}

export interface TopCustomersResponse {
  customers_with_multiple_entries: Customer[];
}

export interface OutstandingBalance {
  customer_name: string;
  outstanding_amount: number;
}

export interface MetricCard {
  title: string;
  value: number;
  icon: string;
  color: string;
  trend?: number;
}