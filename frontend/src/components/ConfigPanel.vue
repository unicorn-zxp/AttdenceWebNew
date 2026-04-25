<template>
  <div class="config-panel">
    <h3 class="panel-title">
      <el-icon><Setting /></el-icon> 计算配置
    </h3>

    <div class="config-content">
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
        @change="store.updateConfig"
        class="dark-slider"
      />

      <div class="rules-card">
        <div class="rule-line">
          <span class="rule-icon">&#9654;</span>
          早班进位: &le; 07:40 按 07:30 计
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
          加班分界: 16:30 后算加班
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
const tolerance = ref(store.lateTolerance)
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
