import { Component, OnInit } from '@angular/core';
import { StaffService } from '../../services/staff.service';
import { StaffCreate, StaffListItem, StaffUpdate } from '../../models/staff.model';
import { NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../navbar/navbar.component';

@Component({
  selector: 'app-owner-dashboard',
  templateUrl: './owner-dashboard.component.html',
  styleUrls: ['./owner-dashboard.component.css'],
  imports : [NgIf,FormsModule,NgFor,NavbarComponent]
})
export class OwnerDashboardComponent implements OnInit {
  newStaff: StaffCreate = { email: '', password: '', phone_number: '', assigned_role: '' };
  staffList: StaffListItem[] = [];
  staffCreateError = '';
  staffCreateSuccess = false;
  showDetailModal = false;
  selectedStaff: StaffListItem | null = null;
  selectedStaffEdit: StaffUpdate = {};
  selectedStaffIndex: number | null = null;
  staffUpdateMsg = '';
  staffUpdateError = '';

  constructor(private staffService: StaffService) {}

  ngOnInit() {
    this.fetchStaffList();
  }

  fetchStaffList() {
    this.staffService.getAllStaff().subscribe({
      next: data => this.staffList = data,
      error: () => this.staffList = []
    });
  }

  createStaff() {
    this.staffCreateError = '';
    this.staffCreateSuccess = false;
    this.staffService.createStaff(this.newStaff).subscribe({
      next: () => {
        this.staffCreateSuccess = true;
        this.newStaff = { email: '', password: '', phone_number: '', assigned_role: '' };
        this.fetchStaffList();
      },
      error: err => {
        this.staffCreateError = err.error?.detail || 'Failed to create staff';
      }
    });
  }

  openStaffDetail(staff: StaffListItem, index: number) {
    this.staffUpdateMsg = '';
    this.staffUpdateError = '';
    this.staffService.getStaffDetail(staff.id).subscribe({
      next: detail => {
        this.selectedStaff = detail;
        this.selectedStaffEdit = {
          phone_number: detail.phone_number,
          assigned_role: detail.assigned_role
        };
        this.selectedStaffIndex = index;
        this.showDetailModal = true;
      },
      error: () => {
        this.selectedStaff = null;
        this.selectedStaffEdit = {};
        this.selectedStaffIndex = null;
        this.showDetailModal = false;
      }
    });
  }

  closeDetailModal() {
    this.showDetailModal = false;
    this.selectedStaff = null;
    this.selectedStaffEdit = {};
    this.selectedStaffIndex = null;
    this.staffUpdateMsg = '';
    this.staffUpdateError = '';
  }

  updateStaff() {
    if (!this.selectedStaff) return;
    this.staffUpdateMsg = '';
    this.staffUpdateError = '';
    this.staffService.updateStaff(this.selectedStaff.id, this.selectedStaffEdit).subscribe({
      next: () => {
        this.staffUpdateMsg = 'Staff updated successfully!';
        if (this.selectedStaffIndex !== null) {
          this.staffList[this.selectedStaffIndex] = {
            ...this.staffList[this.selectedStaffIndex],
            ...this.selectedStaffEdit
          };
        }
      },
      error: err => {
        this.staffUpdateError = err.error?.detail || 'Failed to update staff';
      }
    });
  }

  deleteStaff(staff: StaffListItem, index: number) {
    if (!confirm('Are you sure you want to delete this staff?')) return;
    this.staffService.deleteStaff(staff.id).subscribe({
      next: () => {
        this.staffList.splice(index, 1);
      },
      error: () => {
        alert('Failed to delete staff');
      }
    });
  }
}
