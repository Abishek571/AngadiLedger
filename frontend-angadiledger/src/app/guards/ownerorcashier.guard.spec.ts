import { TestBed } from '@angular/core/testing';
import { CanActivateFn } from '@angular/router';

import { ownerorcashierGuard } from './ownerorcashier.guard';

describe('ownerorcashierGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) => 
      TestBed.runInInjectionContext(() => ownerorcashierGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
