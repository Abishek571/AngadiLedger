import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { StaffCreate, StaffListItem, StaffUpdate } from '../models/staff.model';

@Injectable({ providedIn: 'root' })
export class StaffService {
  private apiUrl = 'http://localhost:8000';
  constructor(private http: HttpClient) {}

  getAllStaff(): Observable<StaffListItem[]> {
    return this.http.get<StaffListItem[]>(`${this.apiUrl}/staff/owner/all`);
  }

  createStaff(staff: StaffCreate): Observable<any> {
    return this.http.post(`${this.apiUrl}/staff/owner/add`, staff);
  }

  getStaffDetail(staffId: number): Observable<StaffListItem> {
    return this.http.get<StaffListItem>(`${this.apiUrl}/staff/owner/staffs/${staffId}`);
  }

  updateStaff(staffId: number, update: StaffUpdate): Observable<any> {
    return this.http.put(`${this.apiUrl}/staff/owner/update/${staffId}`, update);
  }

  deleteStaff(staffId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/staff/owner/delete/${staffId}`);
  }
}
