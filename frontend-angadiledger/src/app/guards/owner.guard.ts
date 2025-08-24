import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { jwtDecode } from 'jwt-decode';

export const ownerGuard: CanActivateFn = (route, state) => {
const router = inject(Router);
  const token = localStorage.getItem('access_token');
  if (token) {
    try {
      const decoded:any = jwtDecode(token);
      if (decoded.role === 'owner') {
        return true;
      }
    } catch (e) {}
  }
  router.navigate(['/unauthorized']);
  return false;
};
