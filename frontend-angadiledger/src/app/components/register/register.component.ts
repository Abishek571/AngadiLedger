import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthserviceService,RegisterPayload } from '../../services/authservice.service';
import { NgIf } from '@angular/common';
import { Router, RouterLink } from '@angular/router';


@Component({
  selector: 'app-register',
  imports: [NgIf,ReactiveFormsModule,RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  router=inject(Router)
  registerForm: FormGroup;
  serverError: string | null = null;

  constructor(private fb: FormBuilder, private authService: AuthserviceService) {
    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      role: ['admin', Validators.required],
      business_name: [''],
      phone_number: ['', Validators.required]
    });

    this.registerForm.get('role')?.valueChanges.subscribe(role => {
      const businessNameControl = this.registerForm.get('business_name');
      if (role === 'owner') {
        businessNameControl?.setValidators([Validators.required]);
      }
      else {
        businessNameControl?.clearValidators();
      }
      businessNameControl?.updateValueAndValidity();
    });
  }

  register() {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }
    const payload: RegisterPayload = this.registerForm.value;
    this.authService.register(payload).subscribe({
      next: (res) => {
        this.serverError = null;
      },
      error: (err) => {
        if (err.status === 400 && err.error.detail === 'Email already registered') {
          this.registerForm.get('email')?.setErrors({ emailTaken: true });
        } else {
          this.serverError = err.error?.detail || 'Registration failed. Please try again.';
        }
      }
    });
  }
}
