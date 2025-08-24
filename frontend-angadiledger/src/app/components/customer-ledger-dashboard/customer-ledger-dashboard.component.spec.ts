import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomerLedgerDashboardComponent } from './customer-ledger-dashboard.component';

describe('CustomerLedgerDashboardComponent', () => {
  let component: CustomerLedgerDashboardComponent;
  let fixture: ComponentFixture<CustomerLedgerDashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CustomerLedgerDashboardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CustomerLedgerDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
