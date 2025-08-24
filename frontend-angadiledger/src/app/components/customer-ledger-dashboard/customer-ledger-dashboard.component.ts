import { Component, inject, OnInit } from '@angular/core';
import { CustomerService } from '../../services/customer.service';
import { LedgerEntryService } from '../../services/ledger-entry.service';
import { Customer, CustomerCreate, CustomerUpdate } from '../../models/customer.model';
import { LedgerEntry, LedgerEntryCreate, LedgerEntryUpdate } from '../../models/ledger_entry.model';
import { NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { DatePipe } from '@angular/common';
import { NavbarComponent } from '../navbar/navbar.component';
import { PaymentService } from '../../services/payment.service';

@Component({
  selector: 'app-customer-ledger-dashboard',
  templateUrl: './customer-ledger-dashboard.component.html',
  styleUrls: ['./customer-ledger-dashboard.component.css'],
  imports : [NgIf,FormsModule,NgFor,DatePipe,NavbarComponent]
})
export class CustomerLedgerDashboardComponent implements OnInit {
  router = inject(Router)
  customers: Customer[] = [];
  selectedCustomer: Customer | null = null;
  ledgers: LedgerEntry[] = [];
  showCustomerModal = false;
  showLedgerModal = false;
  isEditCustomer = false;
  isEditLedger = false;
  customerForm: CustomerCreate | CustomerUpdate = {
    name: '', email: '', phone_number: '', business_id: 0, relationship_type: '', notes: ''
  };
  ledgerForm: LedgerEntryCreate | LedgerEntryUpdate = {
    customer_id: 0,entry_type: 'credit', amount: 0, description: '', image_url: ''
  };
  selectedLedger: LedgerEntry | null = null;
  errorMsg = '';
  successMsg = '';

  payments: any[] = [];
  partialSettlements: any[] = [];
  outstandingBalances: any[] = [];

  constructor(
    private customerService: CustomerService,
    private ledgerService: LedgerEntryService,
    private paymentService: PaymentService
  ) {}

  ngOnInit() {
    this.loadCustomers();
    this.loadPartialSettlements();
    this.loadOutstandingBalances();
  }

  selectCustomer(customer: Customer) {
    this.selectedCustomer = customer;
    this.loadLedgers(customer.id);
    this.loadPayments(customer.id);
  }


  loadPayments(customerId: number) {
    this.paymentService.getPaymentsForCustomer(customerId).subscribe({
      next: (data: any[]) => this.payments = data,
      error: () => this.payments = []
    });
  }

  loadPartialSettlements() {
    this.paymentService.getPartialSettlements().subscribe({
      next: (data: any[]) => this.partialSettlements = data,
      error: () => this.partialSettlements = []
    });
  }

  loadOutstandingBalances() {
    this.paymentService.getOutstandingBalances().subscribe({
      next: (data: any[]) => this.outstandingBalances = data,
      error: () => this.outstandingBalances = []
    });
  }

  downloadPaymentsCsv(customerId: number) {
    this.paymentService.downloadPaymentsCsv(customerId).subscribe((blob: Blob | MediaSource) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `payments_customer_${customerId}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    });
  }

  downloadPartialSettlementsCsv() {
    this.paymentService.downloadPartialSettlementsCsv().subscribe((blob: Blob | MediaSource) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `partial_settlements.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    });
  }

  downloadOutstandingBalancesCsv() {
    this.paymentService.downloadOutstandingBalancesCsv().subscribe((blob: Blob | MediaSource) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `outstanding_balances.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    });
  }

  reminderResult: { sent: string[]; failed: { customer: string; reason: string }[] } | null = null;
  sendReminders() {
    this.paymentService.sendOutstandingBalanceReminders().subscribe({
      next: result => {
        this.reminderResult = result;
      },
      error: err => {
        this.reminderResult = { sent: [], failed: [{ customer: 'All', reason: 'Failed to send reminders.' }] };
      }
    });
  }

  loadCustomers() {
    this.customerService.getCustomers().subscribe({
      next: data => this.customers = data,
      error: () => this.customers = []
    });
  }


  loadLedgers(customerId: number) {
    this.ledgerService.getCustomerLedgers(customerId).subscribe({
      next: data => this.ledgers = data,
      error: () => this.ledgers = []
    });
  }

  openCustomerModal(edit = false, customer?: Customer) {
    this.showCustomerModal = true;
    this.isEditCustomer = edit;
    if (edit && customer) {
      this.customerForm = { ...customer };
    } else {
      this.customerForm = { name: '', email: '', phone_number: '', business_id: customer?.business_id || 0, relationship_type: '', notes: '' };
    }
  }

  closeCustomerModal() {
    this.showCustomerModal = false;
    this.isEditCustomer = false;
    this.customerForm = { name: '', email: '', phone_number: '', business_id: 0, relationship_type: '', notes: '' };
    this.errorMsg = '';
    this.successMsg = '';
  }

  saveCustomer() {
    this.errorMsg = '';
    this.successMsg = '';
    if (this.isEditCustomer && this.selectedCustomer) {
      this.customerService.updateCustomer(this.selectedCustomer.id, this.customerForm as CustomerUpdate).subscribe({
        next: updated => {
          this.successMsg = 'Customer updated!';
          this.loadCustomers();
          this.closeCustomerModal();
        },
        error: err => this.errorMsg = err.error?.detail || 'Failed to update customer'
      });
    } else {
      this.customerService.createCustomer(this.customerForm as CustomerCreate).subscribe({
        next: created => {
          this.successMsg = 'Customer created!';
          this.loadCustomers();
          this.closeCustomerModal();
        },
        error: err => this.errorMsg = err.error?.detail || 'Failed to create customer'
      });
    }
  }

  deleteCustomer(customer: Customer) {
    if (!confirm('Delete this customer?')) return;
    this.customerService.deleteCustomer(customer.id).subscribe({
      next: () => {
        this.loadCustomers();
        if (this.selectedCustomer?.id === customer.id) {
          this.selectedCustomer = null;
          this.ledgers = [];
        }
      },
      error: () => alert('Failed to delete customer')
    });
  }

  openLedgerModal(edit = false, ledger?: LedgerEntry) {
    this.showLedgerModal = true;
    this.isEditLedger = edit;
    if (edit && ledger) {
      this.selectedLedger = ledger;
      this.ledgerForm = { ...ledger };
    } else {
      this.ledgerForm = { customer_id: this.selectedCustomer?.id ?? 0, entry_type: 'credit', amount: 0, description: '', image_url: '' };
      this.selectedLedger = null;
    }
  }

  closeLedgerModal() {
    this.showLedgerModal = false;
    this.isEditLedger = false;
    this.ledgerForm = { customer_id: this.selectedCustomer?.id || 0, entry_type: 'credit', amount: 0, description: '', image_url: '' };
    this.errorMsg = '';
    this.successMsg = '';
    this.selectedLedger = null;
  }

  saveLedger() {
    this.errorMsg = '';
    this.successMsg = '';
    if (this.isEditLedger && this.selectedLedger) {
      this.ledgerService.updateLedgerEntry(this.selectedLedger.id, this.ledgerForm as LedgerEntryUpdate).subscribe({
        next: updated => {
          this.successMsg = 'Ledger entry updated!';
          if (this.selectedCustomer) this.loadLedgers(this.selectedCustomer.id);
          this.closeLedgerModal();
        },
        error: err => this.errorMsg = err.error?.detail || 'Failed to update ledger entry'
      });
    } else {
      console.log('Ledger payload:', this.ledgerForm);
      if (!this.ledgerForm.customer_id || this.ledgerForm.customer_id <= 0) {
        this.errorMsg = "Please select a valid customer.";
        return;
      }
      this.ledgerService.createLedgerEntry(this.ledgerForm as LedgerEntryCreate).subscribe({
        next: created => {
          this.successMsg = 'Ledger entry created!';
          if (this.selectedCustomer) this.loadLedgers(this.selectedCustomer.id);
          this.closeLedgerModal();
        },
        error: err => this.errorMsg = err.error?.detail || 'Failed to create ledger entry'
      });
    }
  }

  deleteLedger(ledger: LedgerEntry) {
    if (!confirm('Delete this ledger entry?')) return;
    this.ledgerService.deleteLedgerEntry(ledger.id).subscribe({
      next: () => {
        if (this.selectedCustomer) this.loadLedgers(this.selectedCustomer.id);
      },
      error: () => alert('Failed to delete ledger entry')
    });
  }
}
