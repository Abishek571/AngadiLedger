export interface Customer {
  id: number;
  name: string;
  email: string;
  phone_number: string;
  business_id: number;
  relationship_type: string;
  notes?: string;
  created_by_id: number;
}
export interface CustomerCreate {
  name: string;
  email: string;
  phone_number: string;
  business_id: number;
  relationship_type: string;
  notes?: string;
}
export interface CustomerUpdate {
  name?: string;
  email?: string;
  phone_number?: string;
  relationship_type?: string;
  notes?: string;
}
