import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, firstValueFrom } from 'rxjs';
import { AnalyticsData, TopCustomersResponse } from '../models/analytics.model';

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  private http = inject(HttpClient);
  private readonly API_BASE_URL = 'http://localhost:8000';

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  async getPayables(): Promise<AnalyticsData> {
    const headers = this.getHeaders();
    return firstValueFrom(
      this.http.get<AnalyticsData>(`${this.API_BASE_URL}/analytics/customer/payables/`, { headers })
    );
  }

  async getReceivables(): Promise<AnalyticsData> {
    const headers = this.getHeaders();
    return firstValueFrom(
      this.http.get<AnalyticsData>(`${this.API_BASE_URL}/analytics/customer/receivables/`, { headers })
    );
  }

  async getTopCustomers(): Promise<TopCustomersResponse> {
    const headers = this.getHeaders();
    return firstValueFrom(
      this.http.get<TopCustomersResponse>(`${this.API_BASE_URL}/analytics/customer/multipl_entries/`, { headers })
    );
  }


  getPayables$(): Observable<AnalyticsData> {
    const headers = this.getHeaders();
    return this.http.get<AnalyticsData>(`${this.API_BASE_URL}/analytics/customer/payables/`, { headers });
  }

  getReceivables$(): Observable<AnalyticsData> {
    const headers = this.getHeaders();
    return this.http.get<AnalyticsData>(`${this.API_BASE_URL}/analytics/customer/receivables/`, { headers });
  }

  getTopCustomers$(): Observable<TopCustomersResponse> {
    const headers = this.getHeaders();
    return this.http.get<TopCustomersResponse>(`${this.API_BASE_URL}/analytics/customer/multipl_entries/`, { headers });
  }
}
