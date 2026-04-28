/* AptiTrack Dashboard Charts (Chart.js) */
function initDashboardCharts(categoryData, difficultyData, activityData) {
  // Radar Chart - Category Performance
  const radarCtx = document.getElementById('radar-chart');
  if (radarCtx && categoryData.length > 0) {
    new Chart(radarCtx, {
      type: 'radar',
      data: {
        labels: categoryData.map(c => c.name),
        datasets: [{
          label: 'Accuracy %',
          data: categoryData.map(c => c.accuracy),
          backgroundColor: 'rgba(59,130,246,.2)',
          borderColor: '#3b82f6',
          borderWidth: 2,
          pointBackgroundColor: '#3b82f6',
          pointRadius: 4,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          r: {
            beginAtZero: true, max: 100,
            grid: { color: 'rgba(148,163,184,.15)' },
            ticks: { display: false },
            pointLabels: { color: '#94a3b8', font: { size: 12, family: 'Inter' } },
          }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // Bar Chart - Difficulty Breakdown
  const barCtx = document.getElementById('difficulty-chart');
  if (barCtx && difficultyData.length > 0) {
    new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: difficultyData.map(d => d.level),
        datasets: [
          {
            label: 'Correct', data: difficultyData.map(d => d.correct),
            backgroundColor: '#10b981', borderRadius: 6,
          },
          {
            label: 'Wrong', data: difficultyData.map(d => d.total - d.correct),
            backgroundColor: '#ef4444', borderRadius: 6,
          },
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { family: 'Inter' } } },
          y: { grid: { color: 'rgba(148,163,184,.1)' }, ticks: { color: '#94a3b8' }, beginAtZero: true },
        },
        plugins: { legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } } }
      }
    });
  }

  // Line Chart - Activity Trend
  const lineCtx = document.getElementById('activity-chart');
  if (lineCtx && activityData.length > 0) {
    new Chart(lineCtx, {
      type: 'line',
      data: {
        labels: activityData.map(a => a.date),
        datasets: [{
          label: 'Accuracy %',
          data: activityData.map(a => a.accuracy),
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139,92,246,.1)',
          fill: true, tension: .4, borderWidth: 2,
          pointBackgroundColor: '#8b5cf6', pointRadius: 4,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { family: 'Inter' } } },
          y: { grid: { color: 'rgba(148,163,184,.1)' }, ticks: { color: '#94a3b8' }, beginAtZero: true, max: 100 },
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // Doughnut Chart - Questions by Category
  const doughnutCtx = document.getElementById('category-doughnut');
  if (doughnutCtx && categoryData.length > 0) {
    new Chart(doughnutCtx, {
      type: 'doughnut',
      data: {
        labels: categoryData.map(c => c.name),
        datasets: [{
          data: categoryData.map(c => c.total),
          backgroundColor: categoryData.map(c => c.color),
          borderWidth: 0,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        cutout: '65%',
        plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 12, font: { family: 'Inter' } } } }
      }
    });
  }
}
