<template>
  <div class="upload-panel">
    <h3 class="panel-title">
      <el-icon><FolderOpened /></el-icon> 数据上传
    </h3>

    <!-- Roster -->
    <el-upload
      :auto-upload="true"
      :show-file-list="false"
      accept=".xlsx"
      :http-request="(opts: any) => store.uploadRoster(opts.file)"
      :disabled="store.calculated"
      class="upload-wrapper"
    >
      <div class="upload-item" :class="{ done: store.uploadStatus.roster }">
        <div class="upload-step" :class="{ done: store.uploadStatus.roster }">
          <el-icon v-if="store.uploadStatus.roster"><Check /></el-icon>
          <span v-else>1</span>
        </div>
        <div class="upload-info">
          <span class="upload-label">
            {{ store.uploadStatus.roster ? store.uploadStatus.roster_filename || '花名册已上传' : '上传花名册' }}
          </span>
          <span class="upload-hint">{{ store.uploadStatus.roster ? '花名册' : '.xlsx 劳务人员花名册' }}</span>
        </div>
        <el-icon v-if="store.uploadStatus.roster" class="upload-done-icon"><CircleCheckFilled /></el-icon>
      </div>
    </el-upload>

    <!-- Attendance -->
    <el-upload
      :auto-upload="false"
      :show-file-list="false"
      accept=".xls,.xlsx"
      multiple
      :on-change="onAttendanceChange"
      :disabled="store.calculated"
      class="upload-wrapper"
    >
      <div class="upload-item" :class="{ done: store.uploadStatus.attendance }">
        <div class="upload-step" :class="{ done: store.uploadStatus.attendance }">
          <el-icon v-if="store.uploadStatus.attendance"><Check /></el-icon>
          <span v-else>2</span>
        </div>
        <div class="upload-info">
          <span class="upload-label">
            {{ store.uploadStatus.attendance
              ? `${store.uploadStatus.attendance_count} 个考勤文件`
              : '上传考勤记录' }}
          </span>
          <span class="upload-hint">
            {{ store.uploadStatus.attendance
              ? (store.uploadStatus.attendance_filenames || []).join(', ')
              : '.xls/.xlsx 可多选' }}
          </span>
        </div>
        <el-icon v-if="store.uploadStatus.attendance" class="upload-done-icon"><CircleCheckFilled /></el-icon>
      </div>
    </el-upload>

    <!-- Ledger -->
    <el-upload
      :auto-upload="true"
      :show-file-list="false"
      accept=".xlsx"
      :http-request="(opts: any) => store.uploadLedger(opts.file)"
      :disabled="store.calculated"
      class="upload-wrapper"
    >
      <div class="upload-item" :class="{ done: store.uploadStatus.ledger }">
        <div class="upload-step" :class="{ done: store.uploadStatus.ledger }">
          <el-icon v-if="store.uploadStatus.ledger"><Check /></el-icon>
          <span v-else>3</span>
        </div>
        <div class="upload-info">
          <span class="upload-label">
            {{ store.uploadStatus.ledger ? store.uploadStatus.ledger_filename || '台账已上传' : '上传工资台账' }}
          </span>
          <span class="upload-hint">{{ store.uploadStatus.ledger ? '工资台账' : '.xlsx 现有工资台账' }}</span>
        </div>
        <el-icon v-if="store.uploadStatus.ledger" class="upload-done-icon"><CircleCheckFilled /></el-icon>
      </div>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()

function onAttendanceChange(_file: any, fileList: any[]) {
  const files = fileList.map((f: any) => f.raw).filter(Boolean)
  if (files.length > 0) {
    store.uploadAttendance(files)
  }
}
</script>

<style scoped>
.panel-title {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-inverse-secondary);
  margin: 0 0 var(--space-4) 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

/* Force el-upload to be full-width block */
.upload-wrapper {
  display: block !important;
  width: 100%;
}
.upload-wrapper :deep(.el-upload) {
  display: block;
  width: 100%;
}

.upload-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: var(--space-3);
  width: 100%;
  box-sizing: border-box;
}
.upload-item:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.18);
}
.upload-item.done {
  background: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.3);
}

.upload-step {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-inverse-secondary);
  flex-shrink: 0;
  transition: all var(--transition-fast);
}
.upload-step.done {
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
}

.upload-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}
.upload-label {
  display: block;
  font-size: var(--text-sm);
  color: var(--color-text-inverse);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.upload-hint {
  display: block;
  font-size: 11px;
  color: var(--color-text-inverse-secondary);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.upload-done-icon {
  color: var(--color-success);
  font-size: 18px;
  flex-shrink: 0;
}
</style>
