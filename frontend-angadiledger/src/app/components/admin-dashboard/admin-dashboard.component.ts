import { Component, inject, OnInit } from '@angular/core';
import { AdminService,Owner,AddOwnerPayload } from '../../services/admin.service';
import { NgFor, NgIf} from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NavbarComponent } from "../navbar/navbar.component";

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css'],
  imports: [NgFor, NgIf, FormsModule, NavbarComponent]
})
export class AdminDashboardComponent implements OnInit {
  router = inject(Router)
  activeView: 'list' | 'add' = 'list';
  owners: Owner[] = [];
  newOwner: AddOwnerPayload = { email: '', password: '', phone_number: '', business_name: '' ,role:'owner'};

  constructor(private adminService: AdminService) {}

  ngOnInit() {
    this.showListOwners();
  }

  showListOwners() {
    this.activeView = 'list';
    this.adminService.getOwners().subscribe({
      next: (owners) => this.owners = owners,
      error: () => alert('Failed to fetch owners')
    });
  }

  showAddOwnerForm() {
    this.activeView = 'add';
    this.newOwner = { email: '', password: '', phone_number: '', business_name: '',role:'' };
  }

  addOwner() {
    this.adminService.addOwner(this.newOwner).subscribe({
      next: () => {
        alert('Owner added!');
        this.showListOwners();
      },
      error: () => alert('Failed to add owner')
    });
  }

  deleteOwner(ownerId: number) {
    if (confirm('Are you sure you want to delete this owner?')) {
      this.adminService.deleteOwner(ownerId).subscribe({
        next: () => {
          alert('Owner deleted!');
          this.showListOwners();
        },
        error: () => alert('Failed to delete owner')
      });
    }
  }
}