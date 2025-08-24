import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';

export interface RegisterPayload {
  email: string;
  password: string;
  username: string;
  role: string;
  business_name?: string;
  phone_number?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthserviceService {
  router = inject(Router)
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  register(payload: RegisterPayload): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/users/register`, payload).pipe(
      catchError(this.handleError)
    );
  }

  login(payload: { email: string; password: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/users/login`, payload);
  }

  private handleError(error: HttpErrorResponse) {
    return throwError(() => error);
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }
   logout() {
    localStorage.removeItem('auth_token');
    this.router.navigate(['/login']);
  }

}

