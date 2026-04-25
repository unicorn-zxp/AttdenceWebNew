<template>
  <div class="charts-grid">
    <!-- Left: Horizontal bar for people count per job -->
    <div class="chart-card">
      <div class="section-title">工种人数分布</div>
      <v-chart :option="countBarOption" autoresize class="chart-canvas" />
    </div>

    <!-- Right: Horizontal bar for salary per job, sorted by value -->
    <div class="chart-card">
      <div class="section-title">各工种工资总额</div>
      <v-chart :option="salaryBarOption" autoresize class="chart-canvas" />
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
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useAttendanceStore } from '@/stores/attendance'

use([BarChart, TooltipComponent, GridComponent, CanvasRenderer])

const store = useAttendanceStore()

const jobStats = computed(() => {
  const countMap: Record<string, number> = {}
  const salaryMap: Record<string, number> = {}
  for (const r of store.salaryData) {
    const job = r.工种 || '未知'
    countMap[job] = (countMap[job] || 0) + 1
    salaryMap[job] = (salaryMap[job] || 0) + r.工资总额
  }
  return { countMap, salaryMap }
})

const palette = [
  '#4F46E5', '#6366F1', '#818CF8',
  '#10B981', '#34D399',
  '#F97316', '#FB923C',
  '#EF4444', '#F87171',
  '#3B82F6', '#60A5FA',
  '#8B5CF6', '#A78BFA',
]

const countBarOption = computed(() => {
  const entries = Object.entries(jobStats.value.countMap)
    .sort((a, b) => a[1] - b[1])
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => `${params[0].name}: ${params[0].value}人`,
    },
    grid: { left: 70, right: 30, top: 10, bottom: 20 },
    xAxis: {
      type: 'value',
      axisLabel: { color: '#94A3B8' },
      splitLine: { lineStyle: { color: '#F1F5F9' } },
    },
    yAxis: {
      type: 'category',
      data: entries.map(e => e[0]),
      axisLabel: { color: '#475569', fontSize: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [{
      type: 'bar',
      data: entries.map((e, i) => ({
        value: e[1],
        itemStyle: {
          color: palette[i % palette.length],
          borderRadius: [0, 4, 4, 0],
        },
      })),
      barMaxWidth: 22,
      label: {
        show: true,
        position: 'right' as const,
        formatter: '{c}人',
        color: '#475569',
        fontSize: 11,
      },
    }],
  }
})

const salaryBarOption = computed(() => {
  const entries = Object.entries(jobStats.value.salaryMap)
    .sort((a, b) => a[1] - b[1])
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => `${params[0].name}<br/>¥${params[0].value.toFixed(2)}`,
    },
    grid: { left: 70, right: 50, top: 10, bottom: 20 },
    xAxis: {
      type: 'value',
      axisLabel: {
        color: '#94A3B8',
        formatter: (v: number) => v >= 10000 ? `${(v / 10000).toFixed(1)}万` : `${(v / 1000).toFixed(0)}k`,
      },
      splitLine: { lineStyle: { color: '#F1F5F9' } },
    },
    yAxis: {
      type: 'category',
      data: entries.map(e => e[0]),
      axisLabel: { color: '#475569', fontSize: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [{
      type: 'bar',
      data: entries.map((e, i) => ({
        value: Math.round(e[1] * 100) / 100,
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: {
            type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: '#4F46E5' },
              { offset: 1, color: '#818CF8' },
            ],
          },
        },
      })),
      barMaxWidth: 22,
      label: {
        show: true,
        position: 'right' as const,
        formatter: (p: any) => `¥${(p.value / 1000).toFixed(1)}k`,
        color: '#475569',
        fontSize: 11,
      },
    }],
  }
})
</script>

<style scoped>
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.chart-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-xs);
  border: 1px solid var(--color-border-light);
}
.chart-canvas {
  height: 320px;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .chart-card {
    padding: var(--space-3);
  }
  .chart-canvas {
    height: 260px;
  }
}
</style>
