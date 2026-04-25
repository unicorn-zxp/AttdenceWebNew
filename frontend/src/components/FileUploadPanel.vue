<template>
  <div>
    <h3 style="margin: 0 0 12px 0; font-size: 15px;">
      <el-icon><FolderOpened /></el-icon> 数据上传
    </h3>

    <!-- Roster -->
    <el-upload
      :auto-upload="true"
      :show-file-list="false"
      accept=".xlsx"
      :http-request="(opts: any) => store.uploadRoster(opts.file)"
      :disabled="store.calculated"
    >
      <el-button
        :type="store.uploadStatus.roster ? 'success' : 'default'"
        style="width: 100%;"
      >
        <el-icon><Document /></el-icon>
        {{ store.uploadStatus.roster ? '花名册已上传' : '上传花名册 (.xlsx)' }}
      </el-button>
    </el-upload>

    <!-- Attendance -->
    <el-upload
      :auto-upload="true"
      :show-file-list="false"
      accept=".xls,.xlsx"
      multiple
      :http-request="(opts: any) => store.uploadAttendance([opts.file])"
      :disabled="store.calculated"
      style="margin-top: 10px; display: block;"
    >
      <el-button
        :type="store.uploadStatus.attendance ? 'success' : 'default'"
        style="width: 100%;"
      >
        <el-icon><Calendar /></el-icon>
        {{ store.uploadStatus.attendance
          ? `考勤已上传 (${store.uploadStatus.attendance_count}个文件)`
          : '上传考勤记录 (.xls/.xlsx，可多选)' }}
      </el-button>
    </el-upload>

    <!-- Ledger -->
    <el-upload
      :auto-upload="true"
      :show-file-list="false"
      accept=".xlsx"
      :http-request="(opts: any) => store.uploadLedger(opts.file)"
      :disabled="store.calculated"
      style="margin-top: 10px; display: block;"
    >
      <el-button
        :type="store.uploadStatus.ledger ? 'success' : 'default'"
        style="width: 100%;"
      >
        <el-icon><Notebook /></el-icon>
        {{ store.uploadStatus.ledger ? '台账已上传' : '上传工资台账 (.xlsx)' }}
      </el-button>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
</script>
