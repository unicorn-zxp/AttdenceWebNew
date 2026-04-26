<template>
  <div class="dashboard">
    <!-- Page Header -->
    <div class="dash-header">
      <div>
        <h2 class="dash-title">
          {{ new Date().getFullYear() }} 年度工资总览
          <el-tag v-if="store.annualData.length > 0" effect="plain" round size="small" class="dash-months-tag">
            {{ store.annualData.length }} 个月数据
          </el-tag>
        </h2>
        <p class="dash-desc">{{ store.activeProject?.name || '默认项目' }} · 全年工资数据汇总</p>
      </div>
      <el-button @click="store.fetchAnnual()" :icon="Refresh" circle size="small" />
    </div>

    <!-- Empty State -->
    <div v-if="store.annualData.length === 0" class="dash-empty">
      <svg class="dash-empty-icon" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="60" cy="60" r="50" fill="#F1F5F9" stroke="#E2E8F0" stroke-width="2"/>
        <rect x="35" y="42" width="50" height="6" rx="3" fill="#CBD5E1"/>
        <rect x="35" y="54" width="38" height="5" rx="2.5" fill="#E2E8F0"/>
        <rect x="35" y="64" width="44" height="5" rx="2.5" fill="#E2E8F0"/>
        <rect x="35" y="74" width="32" height="5" rx="2.5" fill="#E2E8F0"/>
      </svg>
      <h3 class="dash-empty-title">暂无年度数据</h3>
      <p class="dash-empty-desc">请切换到「考勤计算」上传工资台账，系统会自动读取历史月份并显示汇总</p>
    </div>

    <!-- Data View -->
    <template v-else>
      <!-- Grand total KPI cards -->
      <div class="grand-grid">
        <div class="grand-card grand-card--salary">
          <div class="grand-icon">
            <el-icon :size="24"><Money /></el-icon>
          </div>
          <div class="grand-body">
            <span class="grand-label">年度累计工资</span>
            <span class="grand-value grand-value--salary">{{ formatMoney(grandTotal) }}</span>
          </div>
        </div>
        <div class="grand-card grand-card--people">
          <div class="grand-icon">
            <el-icon :size="24"><User /></el-icon>
          </div>
          <div class="grand-body">
            <span class="grand-label">人数峰值</span>
            <span class="grand-value">{{ maxPeople }}<small>人</small></span>
          </div>
        </div>
        <div class="grand-card grand-card--workdays">
          <div class="grand-icon">
            <el-icon :size="24"><Calendar /></el-icon>
          </div>
          <div class="grand-body">
            <span class="grand-label">累计出勤工日</span>
            <span class="grand-value">{{ totalWorkdays.toLocaleString() }}<small>工日</small></span>
          </div>
        </div>
        <div class="grand-card grand-card--overtime">
          <div class="grand-icon">
            <el-icon :size="24"><Timer /></el-icon>
          </div>
          <div class="grand-body">
            <span class="grand-label">累计加班工时</span>
            <span class="grand-value">{{ totalOvertime.toFixed(1) }}<small>小时</small></span>
          </div>
        </div>
      </div>

      <!-- Chart: full width -->
      <div class="dash-card">
        <div class="dash-card-header">
          <h3 class="section-title" style="margin-bottom:0">月度工资趋势</h3>
        </div>
        <v-chart :option="chartOption" autoresize class="dash-chart" />
      </div>

      <!-- Monthly Detail Table -->
      <div class="dash-card">
        <div class="dash-card-header">
          <h3 class="section-title" style="margin-bottom:0">月度明细</h3>
          <el-tag effect="plain" round size="small">{{ store.annualData.length }} 个月</el-tag>
        </div>
        <el-table :data="store.annualData" stripe size="default">
          <el-table-column prop="month" label="月份" width="80">
            <template #default="{ row }">{{ row.month }}月</template>
          </el-table-column>
          <el-table-column prop="sheet_name" label="工资表" min-width="180" />
          <el-table-column prop="people" label="人数" width="80">
            <template #default="{ row }">{{ row.people }}人</template>
          </el-table-column>
          <el-table-column prop="total_salary" label="工资总额" min-width="120" sortable>
            <template #default="{ row }">
              <strong style="color: var(--color-brand)">{{ formatMoney(row.total_salary) }}</strong>
            </template>
          </el-table-column>
          <el-table-column prop="total_workdays" label="出勤工日" width="100" sortable />
          <el-table-column prop="total_overtime" label="加班工时" width="100" sortable>
            <template #default="{ row }">{{ row.total_overtime }}h</template>
          </el-table-column>
        </el-table>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import {
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useAttendanceStore } from '@/stores/attendance'

use([BarChart, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

const store = useAttendanceStore()

const grandTotal = computed(() =>
  store.annualData.reduce((sum, m) => sum + m.total_salary, 0),
)
const maxPeople = computed(() =>
  Math.max(...store.annualData.map(m => m.people)),
)
const totalWorkdays = computed(() =>
  store.annualData.reduce((sum, m) => sum + m.total_workdays, 0),
)
const totalOvertime = computed(() =>
  store.annualData.reduce((sum, m) => sum + m.total_overtime, 0),
)

function formatMoney(v: number): string {
  if (v >= 10000) return `¥${(v / 10000).toFixed(2)}万`
  return `¥${v.toFixed(2)}`
}

const chartOption = computed(() => {
  const data = store.annualData
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = data[params[0].dataIndex]
        return `<b>${item.month}月</b><br/>工资: ¥${item.total_salary.toFixed(2)}<br/>人数: ${item.people}人<br/>工日: ${item.total_workdays}`
      },
    },
    legend: { show: false },
    grid: { left: 60, right: 20, top: 16, bottom: 28 },
    xAxis: {
      type: 'category',
      data: data.map(m => `${m.month}月`),
      axisLabel: { color: '#475569', fontSize: 12 },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#E2E8F0' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#94A3B8',
        fontSize: 11,
        formatter: (v: number) => v >= 10000 ? `${(v / 10000).toFixed(0)}万` : `${(v / 1000).toFixed(0)}k`,
      },
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      {
        name: '工资总额',
        type: 'bar',
        data: data.map(m => m.total_salary),
        barMaxWidth: 48,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#4F46E5' },
              { offset: 1, color: '#818CF8' },
            ],
          },
        },
        label: {
          show: true,
          position: 'top' as const,
          formatter: (p: any) => p.value >= 10000 ? `${(p.value / 10000).toFixed(1)}万` : '',
          color: '#475569',
          fontSize: 11,
        },
      },
    ],
  }
})
</script>

<style scoped>
.dashboard {
  padding: var(--space-4) 0;
}

.dash-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-5);
}
.dash-title {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.dash-months-tag {
  font-size: 12px;
}
.dash-desc {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  margin: 0;
}

/* ===== Empty State ===== */
.dash-empty {
  text-align: center;
  padding: var(--space-12) 0;
}
.dash-empty-icon {
  width: 120px;
  height: 120px;
  margin-bottom: var(--space-5);
}
.dash-empty-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2) 0;
}
.dash-empty-desc {
  color: var(--color-text-tertiary);
  font-size: var(--text-sm);
  margin: 0;
  max-width: 400px;
  margin: 0 auto;
}

/* ===== KPI Cards ===== */
.grand-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
.grand-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-xs);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}
.grand-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.grand-card--salary {
  background: var(--kpi-indigo-bg);
  border-color: rgba(79, 70, 229, 0.15);
}
.grand-card--people {
  background: var(--kpi-emerald-bg);
  border-color: rgba(16, 185, 129, 0.15);
}
.grand-card--workdays {
  background: var(--kpi-orange-bg);
  border-color: rgba(249, 115, 22, 0.15);
}
.grand-card--overtime {
  background: var(--kpi-red-bg);
  border-color: rgba(239, 68, 68, 0.15);
}

.grand-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: rgba(255,255,255,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.grand-card--salary .grand-icon { color: var(--kpi-indigo); }
.grand-card--people .grand-icon { color: var(--kpi-emerald); }
.grand-card--workdays .grand-icon { color: var(--kpi-orange); }
.grand-card--overtime .grand-icon { color: var(--kpi-red); }

.grand-body {
  flex: 1;
  min-width: 0;
}
.grand-label {
  display: block;
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  margin-bottom: 2px;
}
.grand-value {
  display: block;
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1.15;
}
.grand-value small {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-tertiary);
  margin-left: 2px;
}
.grand-value--salary {
  font-size: 30px;
  color: var(--color-brand);
}

/* ===== Cards ===== */
.dash-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-xs);
  border: 1px solid var(--color-border-light);
  margin-bottom: var(--space-5);
}
.dash-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}
.dash-chart {
  height: 320px;
}

@media (max-width: 1024px) {
  .grand-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 640px) {
  .grand-grid {
    grid-template-columns: 1fr;
  }
  .grand-card {
    padding: var(--space-3);
    gap: var(--space-3);
  }
  .grand-icon {
    width: 40px;
    height: 40px;
  }
  .grand-value {
    font-size: var(--text-xl);
  }
  .grand-value--salary {
    font-size: var(--text-2xl);
  }
  .dash-card {
    padding: var(--space-3);
  }
  .dash-chart {
    height: 240px;
  }
  .dash-header {
    flex-direction: column;
    gap: var(--space-2);
  }
}
</style>
