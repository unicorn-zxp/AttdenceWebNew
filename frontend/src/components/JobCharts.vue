<template>
  <el-row :gutter="16" style="margin-bottom: 20px;">
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header><strong>工种人数分布</strong></template>
        <v-chart :option="pieOption" autoresize style="height: 320px;" />
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header><strong>各工种工资总额</strong></template>
        <v-chart :option="barOption" autoresize style="height: 320px;" />
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useAttendanceStore } from '@/stores/attendance'

use([PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

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

const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']

const pieOption = computed(() => {
  const data = Object.entries(jobStats.value.countMap).map(([name, value]) => ({ name, value }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)' },
    legend: { bottom: 0, type: 'scroll' },
    color: colors,
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{c}人' },
      data,
    }],
  }
})

const barOption = computed(() => {
  const entries = Object.entries(jobStats.value.salaryMap)
    .sort((a, b) => a[1] - b[1])
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => `${params[0].name}<br/>¥${params[0].value.toFixed(2)}` },
    grid: { left: 80, right: 30, top: 20, bottom: 30 },
    xAxis: { type: 'value', axisLabel: { formatter: (v: number) => `¥${(v / 1000).toFixed(0)}k` } },
    yAxis: { type: 'category', data: entries.map(e => e[0]) },
    series: [{
      type: 'bar',
      data: entries.map(e => Math.round(e[1] * 100) / 100),
      itemStyle: { color: '#5470c6', borderRadius: [0, 4, 4, 0] },
      barMaxWidth: 30,
    }],
  }
})
</script>
