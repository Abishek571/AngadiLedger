import { Component, OnInit, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { BaseChartDirective } from 'ng2-charts';
import { 
  Chart, 
  ChartConfiguration, 
  ChartData, 
  ChartEvent,
  ActiveElement,
  ChartType
} from 'chart.js';
import { AnalyticsService } from '../../services/analytics.service';
import { 
  Customer, 
  AnalyticsData, 
  OutstandingBalance, 
  LedgerEntry 
} from '../../models/analytics.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-analytics-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    BaseChartDirective
  ],
  templateUrl: './analytics-dashboard.component.html',
  styleUrls: ['./analytics-dashboard.component.css']
})
export class AnalyticsDashboardComponent implements OnInit {
  router = inject(Router)
  private analyticsService = inject(AnalyticsService);
  private snackBar = inject(MatSnackBar);

  payablesData = signal<AnalyticsData | null>(null);
  receivablesData = signal<AnalyticsData | null>(null);
  topCustomers = signal<Customer[]>([]);
  outstandingBalances = signal<OutstandingBalance[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);

  netBalance = computed(() => {
    const payables = this.payablesData()?.total_business_payable || 0;
    const receivables = this.receivablesData()?.total_business_receivable || 0;
    return payables - receivables;
  });

  totalOutstanding = computed(() => {
    return this.outstandingBalances().reduce((sum, balance) => sum + balance.outstanding_amount, 0);
  });

  outstandingDifference = computed(() => {
    return this.totalOutstanding() - this.netBalance();
  });

  pieChartData = computed<ChartData<'pie'>>(() => ({
    labels: ['Payables', 'Receivables'],
    datasets: [{
      data: [
        this.payablesData()?.total_business_payable || 0,
        this.receivablesData()?.total_business_receivable || 0
      ],
      backgroundColor: ['#ef4444', '#22c55e'],
      borderWidth: 2,
      borderColor: '#ffffff',
      hoverBackgroundColor: ['#dc2626', '#16a34a'],
      hoverBorderColor: '#ffffff'
    }]
  }));

  pieChartOptions: ChartConfiguration<'pie'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          font: {
            size: 14
          },
          usePointStyle: true
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0';
            return `${label}: $${value.toLocaleString()} (${percentage}%)`;
          }
        }
      }
    }
  };

  barChartData = computed<ChartData<'bar'>>(() => ({
    labels: this.topCustomers().slice(0, 10).map(c => 
      c.customer_name.length > 15 ? c.customer_name.substring(0, 15) + '...' : c.customer_name
    ),
    datasets: [
      {
        label: 'Transaction Count',
        data: this.topCustomers().slice(0, 10).map(c => c.ledgers.length),
        backgroundColor: '#3b82f6',
        borderColor: '#1d4ed8',
        borderWidth: 1,
        yAxisID: 'y'
      },
      {
        label: 'Total Amount ($)',
        data: this.topCustomers().slice(0, 10).map(c => c.total_payable),
        backgroundColor: '#10b981',
        borderColor: '#059669',
        borderWidth: 1,
        yAxisID: 'y1'
      }
    ]
  }));

  barChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Customers'
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45
        }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Transaction Count'
        },
        beginAtZero: true
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Amount ($)'
        },
        beginAtZero: true,
        grid: {
          drawOnChartArea: false,
        },
      }
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            if (label.includes('Amount')) {
              return `${label}: $${value.toLocaleString()}`;
            }
            return `${label}: ${value}`;
          }
        }
      }
    }
  };

  displayedColumns: string[] = ['name', 'email', 'entries', 'amount', 'lastTransaction'];

  ngOnInit() {
    this.loadAllData();
  }

  async loadAllData() {
    try {
      this.loading.set(true);
      this.error.set(null);

      const [payables, receivables, customers] = await Promise.all([
        this.analyticsService.getPayables(),
        this.analyticsService.getReceivables(),
        this.analyticsService.getTopCustomers()
      ]);

      this.payablesData.set(payables);
      this.receivablesData.set(receivables);
      this.topCustomers.set(customers.customers_with_multiple_entries || []);

      this.snackBar.open('Data loaded successfully', 'Close', { duration: 3000 });
    } catch (error) {
      console.error('Error loading data:', error);
      this.error.set('Failed to load analytics data');
      this.snackBar.open('Error loading data', 'Close', { duration: 5000 });
    } finally {
      this.loading.set(false);
    }
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    
    if (!file) return;

    this.processFile(file);
  }

  private parseCSV(csv: string): OutstandingBalance[] {
    const lines = csv.split('\n').filter(line => line.trim());
    const balances: OutstandingBalance[] = [];
    

    const startIndex = lines[0] && (lines[0].toLowerCase().includes('customer') || lines[0].toLowerCase().includes('name')) ? 1 : 0;
    
    for (let i = startIndex; i < lines.length; i++) {
      const values = lines[i].split(',');
      if (values.length >= 2) {
        const customerName = values[0]?.trim().replace(/"/g, '') || '';
        const amountStr = values[1]?.trim().replace(/"/g, '').replace(/[$,]/g, '') || '0';
        const amount = parseFloat(amountStr);
        
        if (customerName && !isNaN(amount)) {
          balances.push({
            customer_name: customerName,
            outstanding_amount: amount
          });
        }
      }
    }
    
    return balances;
  }

  getLastTransactionDate(customer: Customer): string {
    if (!customer.ledgers || customer.ledgers.length === 0) {
      return 'N/A';
    }
    
    const sortedLedgers = customer.ledgers.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
    
    return new Date(sortedLedgers[0].created_at).toLocaleDateString();
  }

  refreshData() {
    this.loadAllData();
  }

  getBalanceClass(): string {
    const balance = this.netBalance();
    return balance >= 0 ? 'positive-balance' : 'negative-balance';
  }

  getDifferenceClass(): string {
    const difference = this.outstandingDifference();
    return difference >= 0 ? 'positive-difference' : 'negative-difference';
  }

  triggerFileInput() {
    const fileInput = document.getElementById('csvFileInput') as HTMLInputElement;
    fileInput?.click();
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    const target = event.currentTarget as HTMLElement;
    target.classList.add('drag-over');
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    const target = event.currentTarget as HTMLElement;
    target.classList.remove('drag-over');
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    const target = event.currentTarget as HTMLElement;
    target.classList.remove('drag-over');
    
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      this.processFile(file);
    }
  }

  private processFile(file: File) {
    if (!file.name.endsWith('.csv')) {
      this.snackBar.open('Please select a CSV file', 'Close', { duration: 3000 });
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const csv = e.target?.result as string;
        const balances = this.parseCSV(csv);
        this.outstandingBalances.set(balances);
        this.snackBar.open(`Loaded ${balances.length} outstanding balance records`, 'Close', { duration: 3000 });
      } catch (error) {
        console.error('Error parsing CSV:', error);
        this.snackBar.open('Error parsing CSV file', 'Close', { duration: 3000 });
      }
    };
    reader.readAsText(file);
  }

  onChartClick(event: ChartEvent, active: ActiveElement[]) {
    if (active.length > 0) {
      console.log('Chart clicked:', active);
    }
  }

  onChartHover(event: ChartEvent, active: ActiveElement[]) {
  }
}
