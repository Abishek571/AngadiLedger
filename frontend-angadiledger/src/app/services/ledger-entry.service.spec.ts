import { TestBed } from '@angular/core/testing';

import { LedgerEntryService } from './ledger-entry.service';

describe('LedgerEntryService', () => {
  let service: LedgerEntryService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LedgerEntryService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
