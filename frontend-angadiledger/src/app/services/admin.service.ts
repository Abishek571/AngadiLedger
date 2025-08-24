import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Owner {
  id: number;
  email: string;
  phone_number: string;
  is_verified: boolean;
  business_name: string;
}

export interface AddOwnerPayload {
  email: string;
  password: string;
  phone_number: string;
  business_name: string;
  role:string;
}

@Injectable({ providedIn: 'root' })
export class AdminService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getOwners(): Observable<Owner[]> {
    return this.http.get<Owner[]>(`${this.apiUrl}/admin/owners`);
  }

  addOwner(payload: AddOwnerPayload): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/admin/owners`, payload);
  }

  deleteOwner(ownerId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/admin/admin/owners/${ownerId}`);
  }
}
