<template>
  <div class="config-panel">
    <h3 class="panel-title">
      <el-icon><Setting /></el-icon> 计算配置
    </h3>

    <div class="config-content">
      <!-- 额定工时（灰色标签） -->
      <div class="rated-hours-badge">
        额定工时 <strong>{{ ratedHours }}</strong> 小时
      </div>

      <!-- 时间配置 -->
      <div class="time-config">
        <div class="time-row">
          <span class="time-label">上班时间</span>
          <el-time-select
            v-model="workStartTime"
            :start="'05:00'"
            :step="'00:30'"
            :end="'12:00'"
            placeholder="上班"
            :disabled="store.calculated"
            :clearable="false"
            teleported
            @change="onTimeChange"
            class="dark-time-select"
          />
        </div>
        <div class="time-row">
          <span class="time-label">下班时间</span>
          <el-time-select
            v-model="workEndTime"
            :start="'14:00'"
            :step="'00:30'"
            :end="'23:00'"
            placeholder="下班"
            :disabled="store.calculated"
            :clearable="false"
            teleported
            @change="onTimeChange"
            class="dark-time-select"
          />
        </div>
        <div class="time-row">
          <span class="time-label">休息开始</span>
          <el-time-select
            v-model="breakStart"
            :start="'10:00'"
            :step="'00:30'"
            :end="'15:00'"
            placeholder="休息开始"
            :disabled="store.calculated"
            :clearable="false"
            teleported
            @change="onTimeChange"
            class="dark-time-select"
          />
        </div>
        <div class="time-row">
          <span class="time-label">休息结束</span>
          <el-time-select
            v-model="breakEnd"
            :start="'11:00'"
            :step="'00:30'"
            :end="'16:00'"
            placeholder="休息结束"
            :disabled="store.calculated"
            :clearable="false"
            teleported
            @change="onTimeChange"
            class="dark-time-select"
          />
        </div>
      </div>

      <!-- 晚班容差 -->
      <div class="tolerance-section">
        <div class="tolerance-display">
          <span class="tolerance-label">晚班弹性容差</span>
          <span class="tolerance-value">{{ tolerance }}<small>分钟</small></span>
        </div>

        <el-slider
          v-model="tolerance"
          :min="1"
          :max="15"
          :step="1"
          :show-tooltip="true"
          :format-tooltip="(val: number) => val + ' 分钟'"
          :disabled="store.calculated"
          @change="onToleranceChange"
          class="dark-slider"
        />
      </div>

      <!-- 规则说明 -->
      <div class="rules-card">
        <div class="rule-line">
          <span class="rule-icon">&#9654;</span>
          早班进位: &le; {{ workStartTime }}+10分钟 → {{ workStartTime }}，早到不算工时
        </div>
        <div class="rule-line">
          <span class="rule-icon">&#9654;</span>
          晚班补齐: &le; {{ tolerance }}分钟 补至整点/半点
        </div>
        <div class="rule-line">
          <span class="rule-icon">&#9654;</span>
          工时取整: 按半小时向下取整
        </div>
        <div class="rule-line">
          <span class="rule-icon">&#9654;</span>
          加班分界: {{ workEndTime }} 后算加班
        </div>
        <div class="rule-line">
          <span class="rule-icon">&#9654;</span>
          工资公式: 额定内 (日工资+2&times;时薪)/{{ ratedHours }}h &times; 实际工时，超出按时薪
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
const tolerance = ref(store.lateTolerance)
const workStartTime = ref(store.workStartTime)
const workEndTime = ref(store.workEndTime)
const breakStart = ref(store.breakStart)
const breakEnd = ref(store.breakEnd)

const ratedHours = computed(() => {
  const ws = timeToMins(workStartTime.value)
  const we = timeToMins(workEndTime.value)
  const bs = timeToMins(breakStart.value)
  const be = timeToMins(breakEnd.value)
  const total = we - ws
  const overlap = Math.max(0, Math.min(we, be) - Math.max(ws, bs))
  return ((total - overlap) / 60).toFixed(1)
})

function timeToMins(t: string): number {
  const [h, m] = t.split(':').map(Number)
  return h * 60 + m
}

function onTimeChange() {
  store.updateConfig({
    work_start_time: workStartTime.value,
    work_end_time: workEndTime.value,
    break_start: breakStart.value,
    break_end: breakEnd.value,
  })
}

function onToleranceChange(val: number) {
  store.updateConfig({ late_tolerance: val })
}
</script>

<style scoped>
.config-panel {
}
.panel-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-inverse-secondary);
  margin: 0 0 var(--space-4) 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.config-content {
  padding: 0;
}

.rated-hours-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-4);
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  color: var(--color-text-inverse-secondary);
  user-select: none;
}
.rated-hours-badge strong {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-brand-lighter);
}

.time-config {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.time-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.time-label {
  font-size: var(--text-sm);
  color: var(--color-text-inverse-secondary);
  flex-shrink: 0;
  min-width: 70px;
}

.dark-time-select {
  flex: 1;
  min-width: 0;
}
:deep(.dark-time-select .el-input__wrapper) {
  background: rgba(255,255,255,0.08);
  box-shadow: none;
  border: 1px solid rgba(255,255,255,0.12);
}
:deep(.dark-time-select .el-input__inner) {
  color: var(--color-text-inverse-primary);
  font-size: var(--text-sm);
}

.tolerance-section {
  margin-bottom: var(--space-2);
}

.tolerance-display {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}
.tolerance-label {
  font-size: var(--text-sm);
  color: var(--color-text-inverse-secondary);
}
.tolerance-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-brand-lighter);
  line-height: 1;
}
.tolerance-value small {
  font-size: var(--text-xs);
  font-weight: 400;
  margin-left: 2px;
}

/* Dark slider overrides */
.dark-slider {
  --el-slider-main-bg-color: var(--color-brand-lighter);
  --el-slider-runway-bg-color: rgba(255,255,255,0.12);
}
:deep(.el-slider__button) {
  border-color: var(--color-brand-lighter) !important;
  background: var(--color-brand-lighter) !important;
  width: 16px !important;
  height: 16px !important;
}
:deep(.el-slider__bar) {
  background: var(--color-brand-lighter);
}

.rules-card {
  margin-top: var(--space-4);
  padding: var(--space-3);
  background: rgba(255,255,255,0.05);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255,255,255,0.06);
}
.rule-line {
  font-size: 12px;
  color: var(--color-text-inverse-secondary);
  line-height: 1.9;
  display: flex;
  align-items: flex-start;
  gap: var(--space-1);
}
.rule-icon {
  color: var(--color-brand-lighter);
  font-size: 8px;
  margin-top: 5px;
  flex-shrink: 0;
}
</style>
