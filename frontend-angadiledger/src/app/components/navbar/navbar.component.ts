import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgIf } from '@angular/common';
import { Router } from '@angular/router';

interface PersonalDetail {
  email: string;
  phone_number: string;
}

interface BusinessDetail {
  email: string;
  business_name?: string | null;
  assigned_role?: string | null;
}

interface UserProfileView {
  personal: PersonalDetail;
  business: BusinessDetail;
}

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css'],
  imports:[NgIf]
})
export class NavbarComponent {
  router = inject(Router)
  showProfileMenu = false;
  profile: UserProfileView | null = null;
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  toggleProfileMenu() {
    this.showProfileMenu = !this.showProfileMenu;
    if (this.showProfileMenu && !this.profile) {
      this.fetchProfile();
    }
  }

  fetchProfile() {
    this.http.get<UserProfileView>(`${this.apiUrl}/profile/details`).subscribe({
      next: (data) => this.profile = data,
      error: () => this.profile = {
        personal: { email: 'Unknown', phone_number: 'Unknown' },
        business: { email: '', business_name: null, assigned_role: null }
      }
    });
  }
  logout() {
    localStorage.removeItem('access_token');
    this.router.navigate(['/login']);
  }
  goToAnalticsDashBoard(){
    this.router.navigate(['/analytics-dashboard'])
  }
  goToCustomerLedger() {
    this.router.navigate(['/customer-ledger-dashboard']);
  }
}
