
export interface Payment {
  customer_name: string;
  amount: number;
  method: string;
  reference: string;
}

export interface PartialSettlement {
  customer_name: string;
  amount: number;
  date: string;
}

export interface OutstandingBalance {
  customer_name: string;
  balance: number;
  contact: string;
}
