import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { LedgerEntry, LedgerEntryCreate, LedgerEntryUpdate } from '../models/ledger_entry.model';

@Injectable({ providedIn: 'root' })
export class LedgerEntryService {
  private apiUrl = 'http://localhost:8000';
  constructor(private http: HttpClient) {}

  getLedgerEntry(id: number): Observable<LedgerEntry> {
    return this.http.get<LedgerEntry>(`${this.apiUrl}/ledger/${id}`);
  }

  createLedgerEntry(data: LedgerEntryCreate): Observable<LedgerEntry> {
    return this.http.post<LedgerEntry>(`${this.apiUrl}/ledger/`, data);
  }

  updateLedgerEntry(id: number, data: LedgerEntryUpdate): Observable<LedgerEntry> {
    return this.http.put<LedgerEntry>(`${this.apiUrl}/ledger/${id}`, data);
  }

  deleteLedgerEntry(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/ledger/${id}`);
  }

  getCustomerLedgers(customerId: number): Observable<LedgerEntry[]> {
    return this.http.get<LedgerEntry[]>(`${this.apiUrl}/customers/${customerId}/ledgers/`);
  }

  getBusinessLedgers(businessId: number): Observable<LedgerEntry[]> {
    return this.http.get<LedgerEntry[]>(`${this.apiUrl}/businesses/${businessId}/ledgers/`);
  }
}
