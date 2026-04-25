<template>
  <div v-if="store.calculated" class="alert-section">
    <!-- Warning Banner -->
    <div
      v-if="store.abnormalCount > 0"
      class="alert-card alert-warning"
      @click="expanded = !expanded"
    >
      <div class="alert-header">
        <div class="alert-header-left">
          <el-icon :size="18"><WarningFilled /></el-icon>
          <span class="alert-title">共 {{ store.abnormalCount }} 人存在异常</span>
        </div>
        <el-icon class="alert-toggle" :class="{ expanded }">
          <ArrowDown />
        </el-icon>
      </div>
      <transition name="slide-up">
        <div v-if="expanded" class="alert-body" @click.stop>
          <el-table
            :data="store.abnormalRecords"
            size="small"
            stripe
            :max-height="220"
          >
            <el-table-column prop="序号" label="序号" min-width="50" />
            <el-table-column prop="姓名" label="姓名" min-width="70" />
            <el-table-column prop="工种" label="工种" min-width="70" />
            <el-table-column prop="出勤工日" label="出勤工日" min-width="70" />
            <el-table-column prop="加班工时" label="加班工时" min-width="70" />
            <el-table-column prop="备注" label="备注" min-width="140" />
          </el-table>
        </div>
      </transition>
    </div>

    <!-- Success Banner -->
    <div v-else class="alert-card alert-success">
      <div class="alert-header">
        <div class="alert-header-left">
          <el-icon :size="18"><CircleCheckFilled /></el-icon>
          <span class="alert-title">所有人员均有工资标准，无异常</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
const expanded = ref(false)
</script>

<style scoped>
.alert-section {
  margin-bottom: var(--space-5);
}

.alert-card {
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.alert-card:hover {
  box-shadow: var(--shadow-sm);
}

.alert-warning {
  background: var(--color-warning-light);
  border-left: 4px solid var(--color-warning);
  color: #92400E;
}
.alert-success {
  background: var(--color-success-light);
  border-left: 4px solid var(--color-success);
  color: #065F46;
  cursor: default;
}

.alert-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.alert-header-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.alert-title {
  font-weight: 600;
  font-size: var(--text-base);
}
.alert-toggle {
  transition: transform var(--transition-fast);
}
.alert-toggle.expanded {
  transform: rotate(180deg);
}

.alert-body {
  margin-top: var(--space-3);
  cursor: default;
}

@media (max-width: 640px) {
  .alert-card {
    padding: var(--space-3);
  }
}
</style>
