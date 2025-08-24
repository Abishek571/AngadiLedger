export interface StaffCreate {
  email: string;
  password: string;
  phone_number: string;
  assigned_role: string;
}

export interface StaffListItem {
  id: number;
  email: string;
  phone_number: string;
  role: string;
  assigned_role: string;
  business_name: string;
}

export interface StaffUpdate {
  phone_number?: string;
  assigned_role?: string;
}
