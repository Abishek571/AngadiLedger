import { Routes } from '@angular/router';
import { RegisterComponent } from './components/register/register.component';
import { LoginComponent } from './components/login/login.component';
import { AdminDashboardComponent } from './components/admin-dashboard/admin-dashboard.component';
import { adminGuard } from './guards/admin.guard';
import { OwnerDashboardComponent } from './components/owner-dashboard/owner-dashboard.component';
import { ownerGuard } from './guards/owner.guard';
import { CustomerLedgerDashboardComponent } from './components/customer-ledger-dashboard/customer-ledger-dashboard.component';
import { ownerorcashierGuard } from './guards/ownerorcashier.guard';
import { authGuard } from './guards/auth.guard';
import { AnalyticsDashboardComponent } from './components/analytics-dashboard/analytics-dashboard.component';

export const routes: Routes = [
 { path: '', component: LoginComponent }, 
  {path:'login',component:LoginComponent},
  { path: 'register', component: RegisterComponent,canActivate:[adminGuard,authGuard] },
  {path:'admin-dashboard',component:AdminDashboardComponent,canActivate:[authGuard,adminGuard]},
  {path:'owner-dashboard',component:OwnerDashboardComponent,canActivate:[authGuard,ownerGuard]},
  {path:'customer-ledger-dashboard',component:CustomerLedgerDashboardComponent,canActivate:[authGuard,ownerorcashierGuard]},
  {path:'analytics-dashboard',component:AnalyticsDashboardComponent,canActivate:[authGuard,ownerorcashierGuard]}
];
