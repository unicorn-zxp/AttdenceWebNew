<template>
  <div class="kpi-grid">
    <div class="kpi-card stagger-item" style="--kpi-color: var(--kpi-indigo); --kpi-bg: var(--kpi-indigo-bg);">
      <div class="kpi-icon">
        <el-icon :size="22"><User /></el-icon>
      </div>
      <div class="kpi-body">
        <span class="kpi-label">结算人数</span>
        <span class="kpi-value">{{ store.overview.total_people }}<small>人</small></span>
      </div>
    </div>

    <div class="kpi-card stagger-item" style="--kpi-color: var(--kpi-emerald); --kpi-bg: var(--kpi-emerald-bg);">
      <div class="kpi-icon">
        <el-icon :size="22"><Money /></el-icon>
      </div>
      <div class="kpi-body">
        <span class="kpi-label">工资总额</span>
        <span class="kpi-value">¥{{ store.overview.total_salary.toFixed(2) }}</span>
      </div>
    </div>

    <div class="kpi-card stagger-item" style="--kpi-color: var(--kpi-orange); --kpi-bg: var(--kpi-orange-bg);">
      <div class="kpi-icon">
        <el-icon :size="22"><Calendar /></el-icon>
      </div>
      <div class="kpi-body">
        <span class="kpi-label">总出勤工日</span>
        <span class="kpi-value">{{ store.overview.total_workdays }}<small>工日</small></span>
      </div>
    </div>

    <div class="kpi-card stagger-item" style="--kpi-color: var(--kpi-red); --kpi-bg: var(--kpi-red-bg);">
      <div class="kpi-icon">
        <el-icon :size="22"><Timer /></el-icon>
      </div>
      <div class="kpi-body">
        <span class="kpi-label">总加班工时</span>
        <span class="kpi-value">{{ store.overview.total_overtime.toFixed(1) }}<small>小时</small></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.kpi-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  box-shadow: var(--shadow-xs);
  border: 1px solid var(--color-border-light);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  cursor: default;
}
.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--kpi-bg);
  color: var(--kpi-color);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-body {
  flex: 1;
  min-width: 0;
}
.kpi-label {
  display: block;
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-1);
}
.kpi-value {
  display: block;
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.1;
}
.kpi-value small {
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--color-text-tertiary);
  margin-left: 2px;
}

@media (max-width: 1280px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 640px) {
  .kpi-card {
    padding: var(--space-3);
    gap: var(--space-2);
  }
  .kpi-icon-circle {
    width: 36px;
    height: 36px;
  }
  .kpi-value {
    font-size: var(--text-lg);
  }
  .kpi-label {
    font-size: var(--text-xs);
  }
}
</style>
