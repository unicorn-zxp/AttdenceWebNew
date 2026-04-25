<template>
  <div v-if="store.annualData.length > 0" class="year-summary">
    <div class="year-header">
      <h3 class="section-title" style="margin-bottom:0">{{ new Date().getFullYear() }} 年度工资汇总</h3>
      <el-tag effect="plain" round size="small">{{ store.annualData.length }} 个月</el-tag>
    </div>

    <!-- Grand total KPI cards -->
    <div class="grand-grid">
      <div class="grand-card grand-card--salary">
        <div class="grand-icon">
          <el-icon :size="22"><Money /></el-icon>
        </div>
        <div class="grand-body">
          <span class="grand-label">年度累计工资</span>
          <span class="grand-value grand-value--salary">{{ formatMoney(grandTotal) }}</span>
        </div>
      </div>
      <div class="grand-card grand-card--people">
        <div class="grand-icon">
          <el-icon :size="22"><User /></el-icon>
        </div>
        <div class="grand-body">
          <span class="grand-label">人数峰值</span>
          <span class="grand-value">{{ maxPeople }}<small>人</small></span>
        </div>
      </div>
      <div class="grand-card grand-card--workdays">
        <div class="grand-icon">
          <el-icon :size="22"><Calendar /></el-icon>
        </div>
        <div class="grand-body">
          <span class="grand-label">累计出勤工日</span>
          <span class="grand-value">{{ totalWorkdays.toLocaleString() }}<small>工日</small></span>
        </div>
      </div>
      <div class="grand-card grand-card--overtime">
        <div class="grand-icon">
          <el-icon :size="22"><Timer /></el-icon>
        </div>
        <div class="grand-body">
          <span class="grand-label">累计加班工时</span>
          <span class="grand-value">{{ totalOvertime.toFixed(1) }}<small>小时</small></span>
        </div>
      </div>
    </div>

    <!-- Chart + Table side by side -->
    <div class="year-content">
      <div class="year-chart-area">
        <v-chart :option="chartOption" autoresize class="year-chart" />
      </div>
      <div class="year-table-area">
        <el-table :data="store.annualData" stripe size="small" class="year-table">
          <el-table-column prop="month" label="月份" width="55">
            <template #default="{ row }">{{ row.month }}月</template>
          </el-table-column>
          <el-table-column prop="people" label="人数" width="55">
            <template #default="{ row }">{{ row.people }}人</template>
          </el-table-column>
          <el-table-column prop="total_salary" label="工资总额" min-width="100" sortable>
            <template #default="{ row }">
              <strong style="color: var(--color-brand)">{{ formatMoney(row.total_salary) }}</strong>
            </template>
          </el-table-column>
          <el-table-column prop="total_workdays" label="工日" width="55" sortable />
          <el-table-column prop="total_overtime" label="加班" width="55" sortable>
            <template #default="{ row }">{{ row.total_overtime }}h</template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
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
        return `<b>${item.month}月</b><br/>工资: ¥${item.total_salary.toFixed(2)}<br/>人数: ${item.people}人`
      },
    },
    legend: {
      data: ['工资总额'],
      bottom: 0,
      textStyle: { color: '#64748B', fontSize: 11 },
    },
    grid: { left: 50, right: 16, top: 12, bottom: 32 },
    xAxis: {
      type: 'category',
      data: data.map(m => `${m.month}月`),
      axisLabel: { color: '#475569', fontSize: 11 },
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
    series: [{
      name: '工资总额',
      type: 'bar',
      data: data.map(m => m.total_salary),
      barMaxWidth: 32,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
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
        fontSize: 10,
      },
    }],
  }
})
</script>

<style scoped>
.year-summary {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
  margin-bottom: var(--space-5);
}
.year-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

/* ===== Grand total KPI cards ===== */
.grand-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.grand-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  border: 1px solid var(--color-border-light);
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
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255,255,255,0.6);
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
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-bottom: 2px;
}
.grand-value {
  display: block;
  font-size: var(--text-xl);
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
  font-size: var(--text-2xl);
  color: var(--color-brand);
}

/* ===== Chart + Table layout ===== */
.year-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}
.year-chart {
  height: 240px;
}

@media (max-width: 1024px) {
  .grand-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .year-content {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .grand-grid {
    grid-template-columns: 1fr;
  }
}
</style>
