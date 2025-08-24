import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { NgIf } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { AuthserviceService } from '../../services/authservice.service';
import { jwtDecode } from 'jwt-decode';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule,NgIf,RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  router=inject(Router)
  loginForm: FormGroup;
  serverError: string = '';
  loading = false;
  authService = inject(AuthserviceService)

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  login() {
    if (this.loginForm.invalid) return;

    this.serverError = '';
    this.loading = true;

    const payload = this.loginForm.value;

    this.authService.login(payload).subscribe({
      next: (res) => {
        this.loading = false;
        localStorage.setItem('access_token', res.access_token);
        const decoded:any = jwtDecode(res.access_token);
      if (decoded.role === 'admin') {
        this.router.navigate(['/admin-dashboard']);
      } else if (decoded.role === 'owner') {
        this.router.navigate(['/owner-dashboard']);
      } else if (decoded.role === 'staff' || decoded.role === 'owner') {
        this.router.navigate(['/customer-ledger-dashboard']);
      } else {
        this.router.navigate(['/']);
      }
      },
      error: (err) => {
        this.loading = false;
        if (err.status === 401) {
          this.serverError = 'Invalid credentials. Please try again.';
        } else if (err.status === 403) {
          this.serverError = 'User not verified. Please check your email.';
        } else if (err.error && err.error.detail) {
          this.serverError = err.error.detail;
        } else {
          this.serverError = 'Login failed. Please try again later.';
        }
      }
    });
  }
}
