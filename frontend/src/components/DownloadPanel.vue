<template>
  <div class="download-grid">
    <div class="download-card">
      <div class="download-icon download-icon--primary">
        <el-icon :size="24"><Document /></el-icon>
      </div>
      <div class="download-info">
        <h4 class="download-title">考勤记录汇总</h4>
        <p class="download-desc">每日出勤、加班工时明细汇总</p>
      </div>
      <el-button type="primary" @click="download('attendance-summary')" class="download-btn">
        <el-icon><Download /></el-icon> 下载
      </el-button>
    </div>

    <div class="download-card">
      <div class="download-icon download-icon--success">
        <el-icon :size="24"><Notebook /></el-icon>
      </div>
      <div class="download-info">
        <h4 class="download-title">
          工资台账
          <el-tag v-if="store.sheetName" type="success" size="small" effect="light" class="sheet-tag">
            {{ store.sheetName }}
          </el-tag>
        </h4>
        <p class="download-desc">含新增Sheet的完整工资台账</p>
      </div>
      <el-button type="success" @click="download('ledger')" class="download-btn">
        <el-icon><Download /></el-icon> 下载
      </el-button>
    </div>

    <div class="download-card">
      <div class="download-icon download-icon--warning">
        <el-icon :size="24"><Tickets /></el-icon>
      </div>
      <div class="download-info">
        <h4 class="download-title">上报表</h4>
        <p class="download-desc">按工种汇总的上报数据表</p>
      </div>
      <el-button type="warning" @click="download('report')" class="download-btn">
        <el-icon><Download /></el-icon> 下载
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()

function download(type: string) {
  const url = store.getDownloadUrl(type)
  const link = document.createElement('a')
  link.href = url
  link.click()
  ElMessage.success('开始下载')
}
</script>

<style scoped>
.download-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.download-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-xs);
  border: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-3);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}
.download-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.download-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}
.download-icon--primary {
  background: var(--kpi-indigo-bg);
  color: var(--kpi-indigo);
}
.download-icon--success {
  background: var(--kpi-emerald-bg);
  color: var(--kpi-emerald);
}
.download-icon--warning {
  background: var(--kpi-orange-bg);
  color: var(--kpi-orange);
}

.download-info {
  flex: 1;
}
.download-title {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}
.sheet-tag {
  font-size: 11px;
}
.download-desc {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  margin: 0;
}

.download-btn {
  width: 100%;
}

@media (max-width: 1024px) {
  .download-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .download-card {
    padding: var(--space-3);
  }
  .download-icon {
    width: 40px;
    height: 40px;
  }
}
</style>
